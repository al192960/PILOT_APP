import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

from database import conectar
from excel_exporter import (
    generar_ambos_excel,
    PLANTILLA_PACKING
)
from translations import tr
from ui_branding import mostrar_logo

TEXTOS = {
    "en": {
        "scan_qr": "Scan QR",
        "scan_here": "Scan here:",
        "ready": "Ready. Scan the first QR code.",
        "scanned_pallets": "Scanned pallets",
        "pallet_id": "Pallet ID",
        "destination": "Destination",
        "packaging": "Packaging",
        "weight": "Weight (lb)",
        "lines": "Lines",
        "status": "Status",
        "scanned_at": "Scanned at",
        "items_of_pallet": "Items of selected pallet",
        "line": "Line",
        "material": "Material",
        "description": "Description",
        "quantity": "Quantity",
        "work_order": "Work order",
        "remove_selected": "Remove selected",
        "clear_all": "Clear all",
        "generate_excel": "Generate Excel files",
        "pallets_scanned": "Pallets scanned: {n}",
        "qr_not_recognized": "QR not recognized: {code}",
        "already_scanned": "Already scanned: {pid}",
        "added": "Added: {pid}",
        "removed": "Removed: {pid}",
        "list_cleared": "List cleared.",
        "select_pallet_title": "Select pallet",
        "select_pallet": "Select a pallet from the list first.",
        "clear_confirm": "Remove all scanned pallets from the list?",
        "nothing_title": "Nothing scanned",
        "nothing_message": "Scan at least one QR code first.",
        "select_template": "Select the packing list template",
        "select_folder": "Select destination folder",
        "export_error_title": "Export error",
        "cannot_write": "Cannot write the files. Close them in Excel and try again.",
        "export_done_title": "Export completed",
        "leave_title": "Leave",
        "leave_message": (
            "There are scanned pallets that have not been exported.\n"
            "If you leave, the list will be lost. Continue?"
        ),
    },
    "es": {
        "scan_qr": "Escanear QR",
        "scan_here": "Escanea aquí:",
        "ready": "Listo. Escanea el primer código QR.",
        "scanned_pallets": "Tarimas escaneadas",
        "pallet_id": "ID de tarima",
        "destination": "Destino",
        "packaging": "Empaque",
        "weight": "Peso (lb)",
        "lines": "Líneas",
        "status": "Estado",
        "scanned_at": "Escaneado a las",
        "items_of_pallet": "Materiales de la tarima seleccionada",
        "line": "Línea",
        "material": "Material",
        "description": "Descripción",
        "quantity": "Cantidad",
        "work_order": "Orden de trabajo",
        "remove_selected": "Quitar seleccionada",
        "clear_all": "Limpiar todo",
        "generate_excel": "Generar archivos Excel",
        "pallets_scanned": "Tarimas escaneadas: {n}",
        "qr_not_recognized": "QR no reconocido: {code}",
        "already_scanned": "Ya fue escaneada: {pid}",
        "added": "Agregada: {pid}",
        "removed": "Quitada: {pid}",
        "list_cleared": "Lista limpiada.",
        "select_pallet_title": "Selecciona una tarima",
        "select_pallet": "Primero selecciona una tarima de la lista.",
        "clear_confirm": "¿Quitar todas las tarimas escaneadas de la lista?",
        "nothing_title": "Nada escaneado",
        "nothing_message": "Escanea al menos un código QR primero.",
        "select_template": "Selecciona la plantilla del packing list",
        "select_folder": "Selecciona la carpeta de destino",
        "export_error_title": "Error al exportar",
        "cannot_write": "No se pueden escribir los archivos. Ciérralos en Excel e inténtalo de nuevo.",
        "export_done_title": "Exportación completada",
        "leave_title": "Salir",
        "leave_message": (
            "Hay tarimas escaneadas que no se han exportado.\n"
            "Si sales, la lista se perderá. ¿Continuar?"
        ),
    },
}


class PackingListGenerator:

    """
    Ventana para escanear muchos QR de tarimas (con lector USB que
    escribe como teclado + Enter), mostrarlos en pantalla, guardarlos
    temporalmente en memoria y al final generar los Excel.
    """

    def __init__(
        self,
        ventana,
        usuario_actual,
        volver_menu,
        idioma="en"
    ):

        self.ventana = ventana
        self.usuario_actual = usuario_actual
        self.volver_menu = volver_menu
        self.idioma = idioma

        # Lista temporal en memoria (se pierde al salir)
        # Cada elemento: dict con los datos de la tarima y la hora
        self.escaneados = []

        self.crear_interfaz()



    def t(self, clave, **datos):

        textos = TEXTOS.get(self.idioma, TEXTOS["en"])
        texto = textos.get(clave, TEXTOS["en"].get(clave, clave))

        return texto.format(**datos) if datos else texto

    # ==================================================
    # UTILIDADES
    # ==================================================

    def limpiar_ventana(self):

        for widget in self.ventana.winfo_children():
            widget.destroy()


    def hora_actual(self):

        return datetime.now().strftime("%H:%M:%S")


    def ids_escaneados(self):

        return [p["pallet_id"] for p in self.escaneados]


    # ==================================================
    # INTERFAZ
    # ==================================================

    def crear_interfaz(self):

        self.limpiar_ventana()

        self.ventana.geometry("1100x780")

        mostrar_logo(
            self.ventana,
            ancho=130,
            pady=(4, 2)
        )

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "packing_list_generator"),
            font=("Arial", 20, "bold")
        ).pack(pady=2)

        tk.Label(
            self.ventana,
            text=(
                f"{self.usuario_actual['name']} "
                f"({self.usuario_actual['employee_id']})"
            ),
            font=("Arial", 10)
        ).pack()

        # -----------------------------------
        # CAMPO DE ESCANEO
        # -----------------------------------

        frame_scan = tk.LabelFrame(
            self.ventana,
            text=self.t("scan_qr"),
            padx=15,
            pady=10
        )

        frame_scan.pack(
            fill="x",
            padx=20,
            pady=6
        )

        tk.Label(
            frame_scan,
            text=self.t("scan_here"),
            font=("Arial", 12)
        ).pack(side="left", padx=8)

        self.entrada_scan = tk.Entry(
            frame_scan,
            font=("Arial", 16),
            width=40
        )

        self.entrada_scan.pack(
            side="left",
            padx=8
        )

        self.entrada_scan.bind(
            "<Return>",
            self.procesar_escaneo
        )

        self.etiqueta_estado = tk.Label(
            self.ventana,
            text=self.t("ready"),
            font=("Arial", 12, "bold"),
            fg="gray"
        )

        self.etiqueta_estado.pack(pady=2)

        # -----------------------------------
        # TABLA DE TARIMAS ESCANEADAS
        # -----------------------------------

        frame_tabla = tk.LabelFrame(
            self.ventana,
            text=self.t("scanned_pallets"),
            padx=8,
            pady=8
        )

        frame_tabla.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=4
        )

        columnas = (
            "n",
            "pallet_id",
            "destination",
            "packaging",
            "weight",
            "lines",
            "status",
            "time"
        )

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            height=8,
            selectmode="browse"
        )

        encabezados = {
            "n": ("#", 40),
            "pallet_id": (self.t("pallet_id"), 200),
            "destination": (self.t("destination"), 100),
            "packaging": (self.t("packaging"), 130),
            "weight": (self.t("weight"), 100),
            "lines": (self.t("lines"), 60),
            "status": (self.t("status"), 100),
            "time": (self.t("scanned_at"), 100),
        }

        for clave, (texto, ancho) in encabezados.items():

            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor="center")

        barra = ttk.Scrollbar(
            frame_tabla,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.configure(yscrollcommand=barra.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.mostrar_detalle
        )

        # -----------------------------------
        # DETALLE DE LA TARIMA SELECCIONADA
        # -----------------------------------

        frame_detalle = tk.LabelFrame(
            self.ventana,
            text=self.t("items_of_pallet"),
            padx=8,
            pady=8
        )

        frame_detalle.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=4
        )

        columnas_det = (
            "line",
            "material",
            "description",
            "quantity",
            "work_order"
        )

        self.tabla_detalle = ttk.Treeview(
            frame_detalle,
            columns=columnas_det,
            show="headings",
            height=6
        )

        encabezados_det = {
            "line": (self.t("line"), 60),
            "material": (self.t("material"), 160),
            "description": (self.t("description"), 360),
            "quantity": (self.t("quantity"), 100),
            "work_order": (self.t("work_order"), 160),
        }

        for clave, (texto, ancho) in encabezados_det.items():

            self.tabla_detalle.heading(clave, text=texto)
            self.tabla_detalle.column(clave, width=ancho, anchor="center")

        self.tabla_detalle.pack(fill="both", expand=True)

        # -----------------------------------
        # BOTONES
        # -----------------------------------

        self.etiqueta_total = tk.Label(
            self.ventana,
            font=("Arial", 11, "bold")
        )

        self.etiqueta_total.pack(pady=2)

        frame_botones = tk.Frame(self.ventana)
        frame_botones.pack(pady=4)

        tk.Button(
            frame_botones,
            text=self.t("remove_selected"),
            width=18,
            command=self.quitar_seleccionado
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            frame_botones,
            text=self.t("clear_all"),
            width=14,
            command=self.limpiar_todo
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            frame_botones,
            text=self.t("generate_excel"),
            width=22,
            font=("Arial", 10, "bold"),
            command=self.generar_excels
        ).grid(row=0, column=2, padx=6)

        tk.Button(
            self.ventana,
            text=tr(self.idioma, "back_to_menu"),
            width=22,
            command=self.salir
        ).pack(pady=6)

        self.actualizar_total()
        self.entrada_scan.focus_set()


    # ==================================================
    # BÚSQUEDA DE LA TARIMA ESCANEADA
    # ==================================================

    def buscar_tarima(self, texto):

        """
        Intenta identificar la tarima a partir del texto del QR:
        1) coincide exactamente con pallets.pallet_id
        2) coincide exactamente con pallets.qr_data
        3) el texto contiene algún pallet_id existente
        Devuelve un dict o None.
        """

        # El QR de tarimas es un JSON con la clave "pid".
        try:

            datos_qr = json.loads(texto)

            if isinstance(datos_qr, dict) and datos_qr.get("pid"):
                texto = str(datos_qr["pid"]).strip()

        except (ValueError, TypeError):
            pass

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            consulta = """
                SELECT
                    p.pallet_id,
                    d.code,
                    p.packaging_type,
                    p.weight_lb,
                    p.status,
                    (
                        SELECT COUNT(*)
                        FROM pallet_items i
                        WHERE i.pallet_record_id = p.id
                    )
                FROM pallets p
                JOIN destinations d
                    ON d.id = p.destination_id
            """

            cursor.execute(
                consulta
                + " WHERE p.pallet_id = ? OR p.qr_data = ?",
                (texto, texto)
            )

            fila = cursor.fetchone()

            if fila is None:

                cursor.execute(
                    "SELECT pallet_id FROM pallets "
                    "WHERE pallet_id IS NOT NULL"
                )

                for (pid,) in cursor.fetchall():

                    if pid and pid in texto:

                        cursor.execute(
                            consulta + " WHERE p.pallet_id = ?",
                            (pid,)
                        )

                        fila = cursor.fetchone()
                        break

        finally:
            conexion.close()

        if fila is None:
            return None

        return {
            "pallet_id": fila[0],
            "destination": fila[1],
            "packaging": fila[2],
            "weight": fila[3],
            "status": fila[4],
            "lines": fila[5],
            "time": self.hora_actual(),
        }


    def obtener_items(self, pallet_id):

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                SELECT
                    i.line_no,
                    i.material,
                    m.description,
                    i.quantity,
                    i.work_order
                FROM pallets p
                JOIN pallet_items i
                    ON i.pallet_record_id = p.id
                LEFT JOIN materials m
                    ON m.material_number = i.material
                WHERE p.pallet_id = ?
                ORDER BY i.line_no
            """, (pallet_id,))

            return cursor.fetchall()

        finally:
            conexion.close()


    # ==================================================
    # ESCANEO
    # ==================================================

    def mensaje(self, texto, color):

        self.etiqueta_estado.config(text=texto, fg=color)


    def procesar_escaneo(self, event=None):

        texto = self.entrada_scan.get().strip()

        self.entrada_scan.delete(0, tk.END)

        if not texto:
            return

        tarima = self.buscar_tarima(texto)

        if tarima is None:

            self.mensaje(
                self.t("qr_not_recognized", code=texto[:60]),
                "red"
            )
            self.ventana.bell()
            self.entrada_scan.focus_set()
            return

        if tarima["pallet_id"] in self.ids_escaneados():

            self.mensaje(
                self.t("already_scanned", pid=tarima["pallet_id"]),
                "orange"
            )
            self.ventana.bell()
            self.entrada_scan.focus_set()
            return

        self.escaneados.append(tarima)

        self.refrescar_tabla(
            seleccionar=tarima["pallet_id"]
        )

        self.mensaje(
            self.t("added", pid=tarima["pallet_id"]),
            "green"
        )

        self.entrada_scan.focus_set()


    # ==================================================
    # TABLAS
    # ==================================================

    def refrescar_tabla(self, seleccionar=None):

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for n, t in enumerate(self.escaneados, start=1):

            iid = self.tabla.insert(
                "",
                tk.END,
                iid=t["pallet_id"],
                values=(
                    n,
                    t["pallet_id"],
                    t["destination"],
                    t["packaging"],
                    t["weight"],
                    t["lines"],
                    t["status"],
                    t["time"]
                )
            )

        if seleccionar and self.tabla.exists(seleccionar):

            self.tabla.selection_set(seleccionar)
            self.tabla.see(seleccionar)

        else:

            self.mostrar_detalle()

        self.actualizar_total()


    def mostrar_detalle(self, event=None):

        for item in self.tabla_detalle.get_children():
            self.tabla_detalle.delete(item)

        seleccion = self.tabla.selection()

        if not seleccion:
            return

        for fila in self.obtener_items(seleccion[0]):

            self.tabla_detalle.insert(
                "",
                tk.END,
                values=(
                    fila[0],
                    fila[1],
                    fila[2] or "",
                    fila[3],
                    fila[4]
                )
            )


    def actualizar_total(self):

        self.etiqueta_total.config(
            text=self.t("pallets_scanned", n=len(self.escaneados))
        )


    # ==================================================
    # QUITAR / LIMPIAR
    # ==================================================

    def quitar_seleccionado(self):

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                self.t("select_pallet_title"),
                self.t("select_pallet")
            )
            return

        pid = seleccion[0]

        self.escaneados = [
            t for t in self.escaneados
            if t["pallet_id"] != pid
        ]

        self.refrescar_tabla()
        self.mensaje(self.t("removed", pid=pid), "gray")
        self.entrada_scan.focus_set()


    def limpiar_todo(self):

        if not self.escaneados:
            return

        if not messagebox.askyesno(
            self.t("clear_all"),
            self.t("clear_confirm")
        ):
            return

        self.escaneados = []
        self.refrescar_tabla()
        self.mensaje(self.t("list_cleared"), "gray")
        self.entrada_scan.focus_set()


    # ==================================================
    # EXCEL
    # ==================================================

    def generar_excels(self):

        if not self.escaneados:

            messagebox.showwarning(
                self.t("nothing_title"),
                self.t("nothing_message")
            )
            return

        # Plantilla: la del proyecto, o pedirla si no existe
        ruta_plantilla = PLANTILLA_PACKING

        if not Path(ruta_plantilla).exists():

            ruta_plantilla = filedialog.askopenfilename(
                title=self.t("select_template"),
                filetypes=[("Excel files", "*.xlsx")]
            )

            if not ruta_plantilla:
                return

        carpeta = filedialog.askdirectory(
            title=self.t("select_folder")
        )

        if not carpeta:
            return

        try:

            packing, escaneos = generar_ambos_excel(
                carpeta,
                self.ids_escaneados(),
                ruta_plantilla,
                self.usuario_actual
            )

        except PermissionError:

            messagebox.showerror(
                self.t("export_error_title"),
                self.t("cannot_write")
            )
            return

        except Exception as error:

            messagebox.showerror(self.t("export_error_title"), str(error))
            return

        messagebox.showinfo(
            self.t("export_done_title"),
            f"{packing}\n{escaneos}"
        )

        self.entrada_scan.focus_set()


    # ==================================================
    # SALIR
    # ==================================================

    def salir(self):

        if self.escaneados:

            if not messagebox.askyesno(
                self.t("leave_title"),
                self.t("leave_message")
            ):
                return

        self.volver_menu()
