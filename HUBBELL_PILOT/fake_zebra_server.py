"""
Simula una impresora Zebra en red.

Uso (en una terminal aparte):
    python fake_zebra_server.py

Luego, en otra terminal:
    python zebra_printer.py 127.0.0.1

Cada etiqueta recibida se guarda en la carpeta labels_received/
"""

import socket
from datetime import datetime
from pathlib import Path

HOST = "0.0.0.0"
PUERTO = 9100
CARPETA = Path(__file__).resolve().parent / "labels_received"


def main():

    CARPETA.mkdir(exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:

        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PUERTO))
        servidor.listen()

        print(f"Fake Zebra listening on port {PUERTO}. Ctrl+C to stop.")

        while True:

            conexion, direccion = servidor.accept()

            with conexion:

                datos = b""

                while True:
                    bloque = conexion.recv(4096)
                    if not bloque:
                        break
                    datos += bloque

            sello = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            ruta = CARPETA / f"label_{sello}.zpl"
            ruta.write_bytes(datos)

            print(f"Received {len(datos)} bytes from {direccion[0]} -> {ruta.name}")


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
