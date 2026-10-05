import hashlib
import secrets

from database import conectar


# -----------------------------------
# CREAR HASH DE CONTRASEÑA
# -----------------------------------

def generar_hash(password):

    salt = secrets.token_bytes(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600000
    )

    return salt.hex() + ":" + resultado.hex()


# -----------------------------------
# VERIFICAR CONTRASEÑA
# -----------------------------------

def verificar_password(password, password_hash):

    try:

        salt_hex, hash_hex = password_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        resultado = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            600000
        )

        return secrets.compare_digest(
            resultado,
            bytes.fromhex(hash_hex)
        )

    except (ValueError, TypeError):

        return False


# -----------------------------------
# INICIAR SESIÓN
# -----------------------------------

def iniciar_sesion(employee_id, password):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            employee_id,
            name,
            password_hash,
            role,
            can_create_packing_list,
            active
        FROM users
        WHERE employee_id = ?
    """, (employee_id,))

    usuario = cursor.fetchone()

    conexion.close()

    if usuario is None:
        return None

    (
        user_id,
        employee_id,
        name,
        password_hash,
        role,
        can_create_packing_list,
        active
    ) = usuario

    if active != 1:
        return None

    if not verificar_password(
        password,
        password_hash
    ):
        return None

    return {
        "id": user_id,
        "employee_id": employee_id,
        "name": name,
        "role": role,
        "can_create_packing_list":
            bool(can_create_packing_list)
    }