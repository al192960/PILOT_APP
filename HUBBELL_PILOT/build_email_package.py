from pathlib import Path
from datetime import datetime
import zipfile

PROJECT_DIR = Path(__file__).resolve().parent

ARCHIVE_ROOT = "HUBBELL_PILOT"

REQUIRED_FILES = [
    "main.py",
    "database.py",
    "auth.py",
    "crear_admin.py",
    "admin_panel.py",
    "pid_generator.py",
    "material_importer.py",
    "qr_generator.py",
    "label_generator.py",
    "translations.py",
    "ui_branding.py",
    "maintenance.py",
    "install_maintenance_task.ps1",
    "remove_maintenance_task.ps1",
    "requirements.txt",
    "IT_SETUP.txt",
    "pallets.db",
]

REQUIRED_ASSETS = [
    "assets/hubbell_logo.png",
    "assets/pilot_icon.png",
    "assets/pilot_icon.ico",
]

OPTIONAL_FILES = [
    "prepare_production.py",
    "build_email_package.py",
]

EMPTY_FOLDERS = [
    "qr",
    "labels",
]


def main():
    required_paths = REQUIRED_FILES + REQUIRED_ASSETS

    faltantes = [
        nombre
        for nombre in required_paths
        if not (PROJECT_DIR / nombre).exists()
    ]

    if faltantes:
        print("No se creó el paquete porque faltan estos archivos:")

        for nombre in faltantes:
            print(f"- {nombre}")

        return

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    zip_path = PROJECT_DIR / f"HUBBELL_PILOT_Production_{fecha}.zip"

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archivo_zip:

        for nombre in REQUIRED_FILES:
            ruta = PROJECT_DIR / nombre
            archivo_zip.write(
                ruta,
                arcname=f"{ARCHIVE_ROOT}/{nombre}"
            )

        for nombre in REQUIRED_ASSETS:
            ruta = PROJECT_DIR / nombre
            archivo_zip.write(
                ruta,
                arcname=f"{ARCHIVE_ROOT}/{nombre}"
            )

        for nombre in OPTIONAL_FILES:
            ruta = PROJECT_DIR / nombre

            if ruta.exists():
                archivo_zip.write(
                    ruta,
                    arcname=f"{ARCHIVE_ROOT}/{nombre}"
                )

        for carpeta in EMPTY_FOLDERS:
            info = zipfile.ZipInfo(
                f"{ARCHIVE_ROOT}/{carpeta}/"
            )
            archivo_zip.writestr(info, "")

    print("=" * 62)
    print("HUBBELL PILOT - PAQUETE PARA CORREO CREADO")
    print("=" * 62)
    print(zip_path)


if __name__ == "__main__":
    main()
