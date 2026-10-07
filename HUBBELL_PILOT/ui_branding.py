from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk


PROJECT_DIR = Path(__file__).resolve().parent
LOGO_PATH = PROJECT_DIR / "assets" / "hubbell_logo.png"


def cargar_logo(ancho=220):
    """Carga el logo HUBBELL y lo redimensiona manteniendo proporción."""

    if not LOGO_PATH.exists():
        return None

    imagen = Image.open(LOGO_PATH)
    ancho_original, alto_original = imagen.size

    if ancho_original <= 0 or alto_original <= 0:
        return None

    proporcion = alto_original / ancho_original
    nuevo_alto = int(ancho * proporcion)

    imagen = imagen.resize(
        (ancho, nuevo_alto),
        Image.LANCZOS
    )

    return ImageTk.PhotoImage(imagen)


def mostrar_logo(parent, ancho=220, pady=(10, 10)):
    """Inserta el logo en el contenedor indicado."""

    logo = cargar_logo(ancho)

    if logo is None:
        return None

    label_logo = tk.Label(parent, image=logo)
    label_logo.image = logo
    label_logo.pack(pady=pady)

    return label_logo
