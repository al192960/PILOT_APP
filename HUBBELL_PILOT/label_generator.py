from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CARPETA_PROYECTO = Path(__file__).resolve().parent

CARPETA_QR = CARPETA_PROYECTO / "qr"

CARPETA_LABELS = CARPETA_PROYECTO / "labels"


# -----------------------------------
# CONFIGURACIÓN DE VISTA PREVIA
# -----------------------------------

# La etiqueta física será 4 x 2 pulgadas.
# Esta imagen se usa como vista previa.
ANCHO = 1200
ALTO = 600


# -----------------------------------
# FUENTES
# -----------------------------------

def cargar_fuente(nombre, tamaño):

    ruta = Path("C:/Windows/Fonts") / nombre

    if ruta.exists():

        return ImageFont.truetype(
            str(ruta),
            tamaño
        )

    return ImageFont.load_default()


FUENTE_PID = cargar_fuente(
    "arialbd.ttf",
    72
)

FUENTE_CAMPO = cargar_fuente(
    "arialbd.ttf",
    34
)

FUENTE_VALOR = cargar_fuente(
    "arial.ttf",
    34
)


# -----------------------------------
# GENERAR ETIQUETA
# -----------------------------------

def generar_etiqueta(
    pid,
    destination,
    packaging,
    weight_lb,
    employee_id
):

    CARPETA_LABELS.mkdir(
        parents=True,
        exist_ok=True
    )

    ruta_qr = (
        CARPETA_QR
        / f"{pid}.png"
    )

    if not ruta_qr.exists():

        raise FileNotFoundError(
            f"QR not found: {ruta_qr}"
        )

    imagen = Image.new(
        "RGB",
        (ANCHO, ALTO),
        "white"
    )

    dibujo = ImageDraw.Draw(
        imagen
    )

    # -----------------------------------
    # BORDE
    # -----------------------------------

    dibujo.rectangle(
        (
            10,
            10,
            ANCHO - 10,
            ALTO - 10
        ),
        outline="black",
        width=4
    )

    # -----------------------------------
    # PID
    # -----------------------------------

    bbox = dibujo.textbbox(
        (0, 0),
        pid,
        font=FUENTE_PID
    )

    ancho_pid = (
        bbox[2] - bbox[0]
    )

    x_pid = (
        ANCHO - ancho_pid
    ) // 2

    dibujo.text(
        (x_pid, 30),
        pid,
        font=FUENTE_PID,
        fill="black"
    )

    # Línea separadora

    dibujo.line(
        (
            40,
            125,
            ANCHO - 40,
            125
        ),
        fill="black",
        width=3
    )

    # -----------------------------------
    # DATOS
    # -----------------------------------

    dibujo.text(
        (50, 165),
        "DEST:",
        font=FUENTE_CAMPO,
        fill="black"
    )

    dibujo.text(
        (185, 165),
        str(destination),
        font=FUENTE_VALOR,
        fill="black"
    )

    dibujo.text(
        (50, 230),
        "PKG:",
        font=FUENTE_CAMPO,
        fill="black"
    )

    dibujo.text(
        (185, 230),
        str(packaging),
        font=FUENTE_VALOR,
        fill="black"
    )

    dibujo.text(
        (50, 295),
        "WT:",
        font=FUENTE_CAMPO,
        fill="black"
    )

    dibujo.text(
        (185, 295),
        f"{weight_lb} LB",
        font=FUENTE_VALOR,
        fill="black"
    )

    dibujo.text(
        (50, 360),
        "USER:",
        font=FUENTE_CAMPO,
        fill="black"
    )

    dibujo.text(
        (185, 360),
        str(employee_id),
        font=FUENTE_VALOR,
        fill="black"
    )

    # -----------------------------------
    # QR
    # -----------------------------------

    qr = Image.open(
        ruta_qr
    ).convert(
        "RGB"
    )

    qr_size = 390

    qr = qr.resize(
        (
            qr_size,
            qr_size
        )
    )

    qr_x = (
        ANCHO
        - qr_size
        - 60
    )

    qr_y = 155

    imagen.paste(
        qr,
        (
            qr_x,
            qr_y
        )
    )

    # -----------------------------------
    # GUARDAR
    # -----------------------------------

    ruta_salida = (
        CARPETA_LABELS
        / f"{pid}.png"
    )

    imagen.save(
        ruta_salida
    )

    return ruta_salida