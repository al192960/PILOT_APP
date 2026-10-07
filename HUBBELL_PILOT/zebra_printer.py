import re
import socket
import urllib.request
from datetime import datetime
from pathlib import Path

from database import obtener_configuracion, guardar_configuracion


# ==================================================
# CONFIGURACIÓN
# ==================================================

PUERTO_ZEBRA = 9100
TIMEOUT_SEGUNDOS = 5

# Carpeta donde se guardan las etiquetas en modo simulación
CARPETA_SIMULACION = (
    Path(__file__).resolve().parent / "labels_simulated"
)

# Tamaño de la etiqueta (para la vista previa) y resolución
ETIQUETA_ANCHO_IN = 4
ETIQUETA_ALTO_IN = 2
DPMM = 8          # 8 = 203 dpi, 12 = 300 dpi

MODO_SIMULADO = "SIMULATED"
MODO_REAL = "REAL"


# ==================================================
# AJUSTES (se guardan en la tabla settings)
# ==================================================

def obtener_modo_zebra():

    # Hasta que se configure otra cosa, SIEMPRE simula.
    modo = obtener_configuracion("zebra_mode")

    return MODO_REAL if modo == MODO_REAL else MODO_SIMULADO


def guardar_modo_zebra(modo):

    if modo not in (MODO_SIMULADO, MODO_REAL):
        raise ValueError("Invalid printer mode.")

    guardar_configuracion("zebra_mode", modo)


def obtener_ip_zebra():

    return (obtener_configuracion("zebra_ip") or "").strip()


def guardar_ip_zebra(ip):

    guardar_configuracion("zebra_ip", ip.strip())


# ==================================================
# ENVÍO REAL POR RED
# ==================================================

def imprimir_zpl_red(zpl, ip=None, puerto=PUERTO_ZEBRA):

    ip = (ip or obtener_ip_zebra()).strip()

    if not ip:
        raise ValueError(
            "The printer IP address is not configured."
        )

    try:

        with socket.create_connection(
            (ip, puerto),
            timeout=TIMEOUT_SEGUNDOS
        ) as conexion:

            conexion.sendall(zpl.encode("utf-8"))

    except socket.timeout:

        raise ConnectionError(
            f"The printer at {ip} did not respond. "
            "Check that it is on and on the same network."
        )

    except OSError as error:

        raise ConnectionError(
            f"Could not connect to the printer at {ip}:{puerto} "
            f"({error})."
        )


# ==================================================
# SIMULACIÓN: guarda el ZPL en un archivo
# ==================================================

def guardar_zpl_simulado(zpl, nombre="label"):

    CARPETA_SIMULACION.mkdir(exist_ok=True)

    limpio = re.sub(r"[^A-Za-z0-9_-]", "_", str(nombre))
    sello = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    ruta = CARPETA_SIMULACION / f"{limpio}_{sello}.zpl"
    ruta.write_text(zpl, encoding="utf-8")

    return ruta


# ==================================================
# PUNTO ÚNICO DE IMPRESIÓN
# ==================================================

def imprimir_zpl(zpl, nombre="label"):

    """
    Simulado -> guarda el .zpl y devuelve la ruta.
    Real     -> lo envía a la Zebra y devuelve None.
    Si falla el modo real, lanza excepción (la tarima NO debe
    marcarse como PRINTED).
    """

    if obtener_modo_zebra() == MODO_REAL:

        imprimir_zpl_red(zpl)
        return None

    return guardar_zpl_simulado(zpl, nombre)


# ==================================================
# VISTA PREVIA (necesita internet; usa el servicio gratuito
# Labelary, que convierte ZPL a PNG). Usa solo datos de prueba:
# el contenido de la etiqueta se envía a ese servicio.
# ==================================================

def generar_vista_previa(zpl, ruta_png):

    url = (
        "http://api.labelary.com/v1/printers/"
        f"{DPMM}dpmm/labels/"
        f"{ETIQUETA_ANCHO_IN}x{ETIQUETA_ALTO_IN}/0/"
    )

    solicitud = urllib.request.Request(
        url,
        data=zpl.encode("utf-8"),
        headers={"Accept": "image/png"},
        method="POST"
    )

    with urllib.request.urlopen(solicitud, timeout=15) as respuesta:
        Path(ruta_png).write_bytes(respuesta.read())

    return ruta_png


# ==================================================
# ETIQUETA 4x2 pulgadas a 203 dpi (812 x 406 puntos)
# QR a la izquierda, datos a la derecha.
# Ajusta posiciones/tamaños para que coincida con tu
# etiqueta real (label_generator.py).
# ==================================================

def _escapar_zpl(texto):

    """Protege los caracteres especiales de ZPL (usa ^FH\\)."""

    return (
        str(texto)
        .replace("\\", "\\5C")
        .replace("^", "\\5E")
        .replace("~", "\\7E")
    )


def _magnificacion_qr(qr_data):

    # Más datos = QR más denso = módulos más pequeños para que
    # el QR siga cabiendo en los 406 puntos de alto.
    n = len(qr_data.encode("utf-8"))

    if n <= 300:
        return 5

    if n <= 450:
        return 4

    return 3


def zpl_tarima(
    pid,
    destino,
    embalaje,
    peso_lb,
    empleado,
    qr_data
):

    mag = _magnificacion_qr(qr_data)
    peso = f"{float(peso_lb):g}"

    return (
        "^XA\n"
        "^CI28\n"
        "^PW812\n"
        "^LL406\n"
        "^LH0,0\n"
        f"^FO20,20^BQN,2,{mag}^FH\\^FDMA,{_escapar_zpl(qr_data)}^FS\n"
        f"^FO350,25^A0N,48,48^FH\\^FD{_escapar_zpl(pid)}^FS\n"
        f"^FO350,100^A0N,36,36^FH\\^FDDestino: {_escapar_zpl(destino)}^FS\n"
        f"^FO350,150^A0N,36,36^FH\\^FD{_escapar_zpl(embalaje)}^FS\n"
        f"^FO350,200^A0N,36,36^FH\\^FDPeso: {peso} lb^FS\n"
        f"^FO350,250^A0N,36,36^FH\\^FDEmp: {_escapar_zpl(empleado)}^FS\n"
        "^XZ"
    )


def imprimir_etiqueta_pid(
    pid,
    destino,
    embalaje,
    peso_lb,
    empleado,
    qr_data
):

    """
    Simulado -> guarda el .zpl.  Real -> imprime en la Zebra.
    Lanza excepción si falla el modo real.
    """

    zpl = zpl_tarima(
        pid,
        destino,
        embalaje,
        peso_lb,
        empleado,
        qr_data
    )

    return imprimir_zpl(zpl, nombre=pid)


# ==================================================
# PRUEBAS
#   python zebra_printer.py sim            -> guarda ZPL de prueba
#   python zebra_printer.py preview        -> ZPL + PNG de vista previa
#   python zebra_printer.py 192.168.1.50   -> imprime en la Zebra real
# ==================================================

if __name__ == "__main__":

    import sys

    argumento = sys.argv[1] if len(sys.argv) > 1 else "sim"

    qr_prueba = (
        '{"version":1,"pid":"100726-HUS-0001","destination":"AIKN",'
        '"packaging":"Pallet","weight_lb":50.5,"employee_id":"1001",'
        '"items":[{"material":"1234567","quantity":10.0,'
        '"work_order":"WO123"}]}'
    )

    zpl = zpl_tarima(
        "100726-HUS-0001", "AIKN", "Pallet", 50.5, "1001", qr_prueba
    )

    if argumento in ("sim", "preview"):

        ruta = guardar_zpl_simulado(zpl, "100726-HUS-0001")
        print("ZPL saved:", ruta)

        if argumento == "preview":

            try:
                png = generar_vista_previa(zpl, ruta.with_suffix(".png"))
                print("Preview saved:", png)
            except Exception as error:
                print("Preview failed (needs internet):", error)

    else:

        try:
            imprimir_zpl_red(zpl, argumento)
            print(f"Label sent to {argumento}:{PUERTO_ZEBRA}")
        except Exception as error:
            print("ERROR:", error)
            raise SystemExit(1)

        guardar_ip_zebra(argumento)
        guardar_modo_zebra(MODO_REAL)
        print("IP saved and mode set to REAL.")
