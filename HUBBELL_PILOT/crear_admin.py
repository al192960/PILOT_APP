from datetime import datetime

from database import crear_base_datos, conectar
from auth import generar_hash


def crear_admin():

    crear_base_datos()

    print()
    print("==============================")
    print(" CREAR ADMINISTRADOR INICIAL")
    print("==============================")
    print()

    employee_id = input(
        "Employee ID: "
    ).strip()

    nombre = input(
        "Nombre completo: "
    ).strip()

    password = input(
        "Contraseña: "
    ).strip()

    if not employee_id:

        print()
        print("ERROR: Employee ID obligatorio.")
        return

    if not nombre:

        print()
        print("ERROR: Nombre obligatorio.")
        return

    if not password:

        print()
        print("ERROR: Contraseña obligatoria.")
        return

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE employee_id = ?
    """, (employee_id,))

    existente = cursor.fetchone()

    if existente is not None:

        conexion.close()

        print()
        print(
            "ERROR: Ese Employee ID "
            "ya existe."
        )

        return

    password_hash = generar_hash(password)

    fecha = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    cursor.execute("""
        INSERT INTO users (
            employee_id,
            name,
            password_hash,
            role,
            can_create_packing_list,
            active,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        nombre,
        password_hash,
        "ADMIN",
        1,
        1,
        fecha
    ))

    conexion.commit()
    conexion.close()

    print()
    print("Administrador creado correctamente.")
    print("Employee ID:", employee_id)
    print("Rol: ADMIN")
    print(
        "Packing List Generator: permitido"
    )


if __name__ == "__main__":

    crear_admin()