import qrcode

from pathlib import Path
from qrcode.exceptions import DataOverflowError


CARPETA_PROYECTO = Path(__file__).resolve().parent

CARPETA_QR = CARPETA_PROYECTO / "qr"


def generar_qr(pid, datos_qr):

    CARPETA_QR.mkdir(
        parents=True,
        exist_ok=True
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=
            qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    qr.add_data(datos_qr)

    try:

        qr.make(
            fit=True
        )

    except DataOverflowError:

        raise ValueError(
            "There is too much information "
            "for one QR code."
        )

    imagen = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    ruta = (
        CARPETA_QR
        / f"{pid}.png"
    )

    imagen.save(ruta)

    return ruta