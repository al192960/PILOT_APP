import sqlite3
from pathlib import Path
from datetime import datetime


# ==================================================
# UBICACIÓN DE LA BASE DE DATOS
# ==================================================

CARPETA_PROYECTO = Path(__file__).resolve().parent
DATABASE = CARPETA_PROYECTO / "pallets.db"


# ==================================================
# CONEXIÓN
# ==================================================

def conectar():

    conexion = sqlite3.connect(DATABASE)

    conexion.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexion


# ==================================================
# CREAR BASE DE DATOS
# ==================================================

def crear_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

    # ==================================================
    # 1. USERS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            employee_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL
                CHECK(
                    role IN (
                        'ADMIN',
                        'GROUP_LEADER',
                        'USER'
                    )
                ),

            can_create_packing_list INTEGER
                NOT NULL
                DEFAULT 0
                CHECK(
                    can_create_packing_list
                    IN (0, 1)
                ),

            active INTEGER
                NOT NULL
                DEFAULT 1
                CHECK(
                    active IN (0, 1)
                ),

            created_at TEXT NOT NULL

        )
    """)

    # ==================================================
    # 2. SETTINGS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            key TEXT PRIMARY KEY,

            value TEXT NOT NULL

        )
    """)

    # ==================================================
    # 3. DESTINATIONS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            code TEXT UNIQUE NOT NULL,

            active INTEGER
                NOT NULL
                DEFAULT 1
                CHECK(
                    active IN (0, 1)
                )

        )
    """)

    # ==================================================
    # 4. MATERIALS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            material_number TEXT UNIQUE NOT NULL,

            description TEXT,

            active INTEGER
                NOT NULL
                DEFAULT 1
                CHECK(
                    active IN (0, 1)
                ),

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        )
    """)

    # ==================================================
    # 5. PALLETS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pallets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            pallet_id TEXT UNIQUE,

            user_id INTEGER NOT NULL,

            destination_id INTEGER NOT NULL,

            packaging_type TEXT NOT NULL
                CHECK(
                    packaging_type IN (
                        'Pallet',
                        'Cajón de madera'
                    )
                ),

            weight_lb REAL NOT NULL
                CHECK(
                    weight_lb > 0
                ),

            status TEXT
                NOT NULL
                DEFAULT 'PENDING'
                CHECK(
                    status IN (
                        'PENDING',
                        'PRINTED'
                    )
                ),

            created_at TEXT NOT NULL,

            printed_at TEXT,

            qr_data TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(destination_id)
                REFERENCES destinations(id)

        )
    """)

    # ==================================================
    # 6. PALLET ITEMS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pallet_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            pallet_record_id INTEGER NOT NULL,

            line_no INTEGER NOT NULL,

            material TEXT NOT NULL,

            quantity REAL NOT NULL
                CHECK(
                    quantity > 0
                ),

            work_order TEXT NOT NULL,

            FOREIGN KEY(pallet_record_id)
                REFERENCES pallets(id)
                ON DELETE CASCADE,

            UNIQUE(
                pallet_record_id,
                line_no
            )

        )
    """)

    # ==================================================
    # 7. PID SEQUENCES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pid_sequences (

            date_code TEXT NOT NULL,

            division_code TEXT NOT NULL,

            last_number INTEGER NOT NULL,

            PRIMARY KEY(
                date_code,
                division_code
            )

        )
    """)

    # ==================================================
    # 8. PRINT HISTORY
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS print_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            pallet_record_id INTEGER NOT NULL,

            printed_by INTEGER NOT NULL,

            printed_at TEXT NOT NULL,

            is_reprint INTEGER
                NOT NULL
                DEFAULT 0
                CHECK(
                    is_reprint IN (0, 1)
                ),

            FOREIGN KEY(pallet_record_id)
                REFERENCES pallets(id),

            FOREIGN KEY(printed_by)
                REFERENCES users(id)

        )
    """)

    # ==================================================
    # 9. PACKING LIST ACCESS LOG
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packing_access_log (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            authorized_by INTEGER NOT NULL,

            authorized_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(authorized_by)
                REFERENCES users(id)

        )
    """)

    # ==================================================
    # CONFIGURACIÓN INICIAL
    # ==================================================

    configuracion_inicial = [

        (
            "division_code",
            "HUS"
        ),

        (
            "inactivity_timeout_minutes",
            "30"
        ),

        (
            "material_database_enabled",
            "0"
        )

    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO settings (
            key,
            value
        )
        VALUES (?, ?)
    """, configuracion_inicial)

    # ==================================================
    # DESTINOS INICIALES
    # ==================================================

    destinos_iniciales = [
        ("AIKN",),
        ("CENT",),
        ("LEED",),
        ("TRIN",)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO destinations (
            code
        )
        VALUES (?)
    """, destinos_iniciales)

    # ==================================================
    # ÍNDICES
    # ==================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_materials_material_number
        ON materials(material_number)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_materials_active
        ON materials(active)
    """)

    # ==================================================
    # GUARDAR
    # ==================================================

    conexion.commit()
    conexion.close()


# ==================================================
# CONFIGURACIÓN
# ==================================================

def obtener_configuracion(clave):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
    """, (
        clave,
    ))

    resultado = cursor.fetchone()

    conexion.close()

    if resultado is None:
        return None

    return resultado[0]


def guardar_configuracion(
    clave,
    valor
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO settings (
            key,
            value
        )
        VALUES (?, ?)

        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value
    """, (
        clave,
        str(valor)
    ))

    conexion.commit()
    conexion.close()


# ==================================================
# MATERIALES
# ==================================================

def material_existe(
    material_number
):

    material_number = (
        str(material_number)
        .strip()
    )

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM materials
        WHERE material_number = ?
          AND active = 1
    """, (
        material_number,
    ))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado is not None


def agregar_o_actualizar_material(
    material_number,
    description=""
):

    material_number = (
        str(material_number)
        .strip()
    )

    description = (
        str(description)
        .strip()
    )

    if not material_number:

        raise ValueError(
            "Material number is required."
        )

    fecha = (
        datetime
        .now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO materials (
            material_number,
            description,
            active,
            created_at,
            updated_at
        )
        VALUES (?, ?, 1, ?, ?)

        ON CONFLICT(material_number)
        DO UPDATE SET

            description =
                excluded.description,

            active = 1,

            updated_at =
                excluded.updated_at
    """, (
        material_number,
        description,
        fecha,
        fecha
    ))

    conexion.commit()
    conexion.close()


def desactivar_material(
    material_number
):

    material_number = (
        str(material_number)
        .strip()
    )

    fecha = (
        datetime
        .now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE materials

        SET
            active = 0,
            updated_at = ?

        WHERE material_number = ?
    """, (
        fecha,
        material_number
    ))

    conexion.commit()

    filas_afectadas = (
        cursor.rowcount
    )

    conexion.close()

    return filas_afectadas > 0


# ==================================================
# PRUEBA
# ==================================================

if __name__ == "__main__":

    crear_base_datos()

    print()
    print(
        "Base de datos actualizada correctamente."
    )

    print(
        "Ubicación:"
    )

    print(
        DATABASE
    )

    print()

    print(
        "Material Database Mode:",
        obtener_configuracion(
            "material_database_enabled"
        )
    )

    print()

    print(
        "Fecha y hora local:",
        datetime.now().strftime(
            "%m/%d/%Y %H:%M:%S"
        )
    )