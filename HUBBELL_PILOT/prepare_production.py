from pathlib import Path
from datetime import datetime
import shutil
import sqlite3

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE = PROJECT_DIR / "pallets.db"
BACKUP_DIR = PROJECT_DIR / "backups"

GENERATED_FOLDERS = [
    PROJECT_DIR / "qr",
    PROJECT_DIR / "labels",
]

RUNTIME_FILES = [
    PROJECT_DIR / "maintenance.log",
    PROJECT_DIR / "maintenance_state.json",
    PROJECT_DIR / ".maintenance.lock",
]


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def limpiar_carpeta(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)

    eliminados = 0

    for item in carpeta.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                eliminados += 1

            elif item.is_dir():
                shutil.rmtree(item)
                eliminados += 1

        except FileNotFoundError:
            pass

    return eliminados


def crear_backup_sqlite():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = (
        BACKUP_DIR
        / f"pallets_before_production_{fecha}.db"
    )

    origen = conectar()
    destino = sqlite3.connect(backup_path)

    try:
        origen.backup(destino)

    finally:
        destino.close()
        origen.close()

    return backup_path


def obtener_admins():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            employee_id,
            name,
            active
        FROM users
        WHERE role = 'ADMIN'
        ORDER BY employee_id
    """)

    admins = cursor.fetchall()

    conexion.close()

    return admins


def mostrar_resumen_actual():
    conexion = conectar()
    cursor = conexion.cursor()

    tablas = [
        "users",
        "materials",
        "pallets",
        "pallet_items",
        "pid_sequences",
        "print_history",
        "packing_access_log",
    ]

    print("\nDATOS ACTUALES")
    print("-" * 48)

    for tabla in tablas:
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            )

            cantidad = cursor.fetchone()[0]

            print(
                f"{tabla:<24} {cantidad:>8}"
            )

        except sqlite3.OperationalError:
            print(
                f"{tabla:<24} NO EXISTE"
            )

    conexion.close()


def preparar_base(admin_employee_id):
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        conexion.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT
                id,
                employee_id,
                name,
                role,
                active
            FROM users
            WHERE employee_id = ?
        """, (
            admin_employee_id,
        ))

        admin = cursor.fetchone()

        if admin is None:
            raise ValueError(
                "El Employee ID indicado no existe."
            )

        if admin[3] != "ADMIN":
            raise ValueError(
                "El usuario indicado no tiene rol ADMIN."
            )

        if admin[4] != 1:
            raise ValueError(
                "El ADMIN indicado está inactivo."
            )

        # Borrar primero tablas dependientes.
        cursor.execute(
            "DELETE FROM print_history"
        )

        cursor.execute(
            "DELETE FROM packing_access_log"
        )

        cursor.execute(
            "DELETE FROM pallet_items"
        )

        cursor.execute(
            "DELETE FROM pallets"
        )

        cursor.execute(
            "DELETE FROM pid_sequences"
        )

        cursor.execute(
            "DELETE FROM materials"
        )

        # Conservar únicamente el ADMIN real.
        cursor.execute("""
            DELETE FROM users
            WHERE employee_id <> ?
        """, (
            admin_employee_id,
        ))

        # Base de materiales vacía al arrancar producción.
        # Se deja OFF para no bloquear el PID Generator
        # hasta importar la base real.
        cursor.execute("""
            INSERT INTO settings (
                key,
                value
            )
            VALUES (
                'material_database_enabled',
                '0'
            )
            ON CONFLICT(key)
            DO UPDATE SET
                value = excluded.value
        """)

        # Reiniciar consecutivos internos de tablas vacías.
        # No se toca el consecutivo de users porque el ADMIN se conserva.
        try:
            cursor.execute("""
                DELETE FROM sqlite_sequence
                WHERE name IN (
                    'materials',
                    'pallets',
                    'pallet_items',
                    'print_history',
                    'packing_access_log'
                )
            """)
        except sqlite3.OperationalError:
            pass

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def main():
    print("=" * 62)
    print("PALLET ID SYSTEM - PREPARAR BASE PARA PRODUCCIÓN")
    print("=" * 62)

    if not DATABASE.exists():
        print(
            "\nERROR: No se encontró pallets.db en:"
        )
        print(DATABASE)
        return

    admins = obtener_admins()

    if not admins:
        print(
            "\nERROR: No existe ningún usuario ADMIN."
        )
        return

    print("\nADMIN disponibles:")
    print("-" * 62)

    for employee_id, name, active in admins:
        estado = (
            "ACTIVO"
            if active == 1
            else "INACTIVO"
        )

        print(
            f"Employee ID: {employee_id} | "
            f"Nombre: {name} | "
            f"{estado}"
        )

    mostrar_resumen_actual()

    print(
        "\nEsta preparación hará lo siguiente:"
    )
    print(
        "- Crear un backup completo de pallets.db."
    )
    print(
        "- Conservar SOLO el ADMIN que tú indiques."
    )
    print(
        "- Conservar settings y destinos."
    )
    print(
        "- Borrar materiales ficticios."
    )
    print(
        "- Borrar pallets/PID e historial de prueba."
    )
    print(
        "- Reiniciar secuencias PID."
    )
    print(
        "- Dejar Material Database Mode en OFF."
    )
    print(
        "- Vaciar qr\\ y labels\\."
    )
    print(
        "- Eliminar archivos temporales de mantenimiento."
    )

    admin_employee_id = input(
        "\nEmployee ID del ADMIN que se conservará: "
    ).strip()

    admins_ids = {
        fila[0]
        for fila in admins
        if fila[2] == 1
    }

    if admin_employee_id not in admins_ids:
        print(
            "\nCANCELADO: el Employee ID indicado "
            "no corresponde a un ADMIN activo."
        )
        return

    confirmacion = input(
        "\nEscribe exactamente PREPARAR para continuar: "
    ).strip()

    if confirmacion != "PREPARAR":
        print(
            "\nOperación cancelada. "
            "No se modificó la base."
        )
        return

    backup_path = crear_backup_sqlite()

    print(
        "\nBackup creado correctamente:"
    )
    print(backup_path)

    try:
        preparar_base(
            admin_employee_id
        )

    except Exception as error:
        print(
            "\nERROR durante la preparación:"
        )
        print(error)
        print(
            "\nTu backup permanece intacto."
        )
        return

    total_generados = 0

    for carpeta in GENERATED_FOLDERS:
        total_generados += (
            limpiar_carpeta(carpeta)
        )

    for archivo in RUNTIME_FILES:
        try:
            if archivo.exists():
                archivo.unlink()
        except Exception:
            pass

    # Recuperar espacio después de borrar datos.
    conexion = conectar()

    try:
        conexion.execute("VACUUM")

    finally:
        conexion.close()

    print("\n" + "=" * 62)
    print("BASE PREPARADA PARA PRODUCCIÓN")
    print("=" * 62)
    print(
        f"ADMIN conservado: {admin_employee_id}"
    )
    print(
        f"Archivos QR/labels eliminados: "
        f"{total_generados}"
    )
    print(
        "Material Database Mode: OFF"
    )
    print(
        "Destinos y configuración: CONSERVADOS"
    )
    print(
        "Pallets, PID, materiales e historial de prueba: LIMPIOS"
    )
    print(
        "\nSiguiente paso: ejecutar build_email_package.py"
    )


if __name__ == "__main__":
    main()
