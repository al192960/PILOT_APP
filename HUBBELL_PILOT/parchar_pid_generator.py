"""
Conecta la impresión Zebra en pid_generator.py.

Uso (desde la carpeta del proyecto):
    python parchar_pid_generator.py

- Hace una copia de respaldo: pid_generator.py.bak
- Agrega el import de imprimir_etiqueta_pid
- Agrega la llamada de impresión en los 3 lugares donde se
  genera la etiqueta (guardar e imprimir, imprimir seleccionado
  y reimprimir último PID)
- Si algo no coincide, NO modifica nada y te lo dice.
- Se puede ejecutar varias veces sin duplicar nada.
"""

import ast
import re
import shutil
import sys
from pathlib import Path

ARCHIVO = Path("pid_generator.py")
IMPORT_NUEVO = "from zebra_printer import imprimir_etiqueta_pid"
ANCLA_IMPORT = "from label_generator import generar_etiqueta"

# generar_etiqueta(pid, destination, packaging, weight_lb, employee_id)
# con o sin paréntesis alrededor de la asignación
PATRON = re.compile(
    r"(?m)^(?P<i>[ ]+)ruta_etiqueta\s*=\s*\(?\s*"
    r"generar_etiqueta\(\s*pid,\s*destination,\s*packaging,\s*"
    r"weight_lb,\s*employee_id\s*\)(?:\s*\))?"
)


def main():

    if not ARCHIVO.exists():
        print("ERROR: pid_generator.py not found in this folder.")
        print("Run this script from the project folder.")
        sys.exit(1)

    original = ARCHIVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in original
    texto = original.replace("\r\n", "\n")

    if "imprimir_etiqueta_pid(" in texto:
        print("pid_generator.py already has the printing calls. Nothing to do.")
        return

    if ANCLA_IMPORT not in texto:
        print(f"ERROR: line '{ANCLA_IMPORT}' not found. File not modified.")
        sys.exit(1)

    coincidencias = PATRON.findall(texto)

    if len(coincidencias) != 3:
        print(
            f"ERROR: expected 3 places to patch but found "
            f"{len(coincidencias)}. File not modified."
        )
        print("Send me the file so I can adjust the script.")
        sys.exit(1)

    def agregar_llamada(m):

        i = m.group("i")

        return (
            m.group(0)
            + "\n\n"
            + f"{i}imprimir_etiqueta_pid(\n"
            + f"{i}    pid,\n"
            + f"{i}    destination,\n"
            + f"{i}    packaging,\n"
            + f"{i}    weight_lb,\n"
            + f"{i}    employee_id,\n"
            + f"{i}    qr_data\n"
            + f"{i})"
        )

    nuevo = PATRON.sub(agregar_llamada, texto)

    nuevo = nuevo.replace(
        ANCLA_IMPORT,
        ANCLA_IMPORT + "\n" + IMPORT_NUEVO,
        1
    )

    # Verificar que el resultado sea Python válido antes de guardar
    try:
        ast.parse(nuevo)
    except SyntaxError as error:
        print("ERROR: the result is not valid Python. File not modified.")
        print(error)
        sys.exit(1)

    shutil.copyfile(ARCHIVO, "pid_generator.py.bak")

    if crlf:
        nuevo = nuevo.replace("\n", "\r\n")

    ARCHIVO.write_bytes(nuevo.encode("utf-8"))

    print("Done. 3 printing calls added to pid_generator.py")
    print("Backup saved as pid_generator.py.bak")


if __name__ == "__main__":
    main()
