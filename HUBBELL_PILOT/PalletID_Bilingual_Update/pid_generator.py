import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime

import json
import math

from database import conectar
from qr_generator import generar_qr
from label_generator import generar_etiqueta
from translations import tr


class PIDGenerator:

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

        self.lineas = []

        self.crear_interfaz()


    # ==================================================
    # UTILIDADES
    # ==================================================

    def limpiar_ventana(self):

        for widget in self.ventana.winfo_children():
            widget.destroy()


    def obtener_destinos(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT code
            FROM destinations
            WHERE active = 1
            ORDER BY code
        """)

        destinos = [
            fila[0]
            for fila in cursor.fetchall()
        ]

        conexion.close()

        return destinos


    # ==================================================
    # MATERIAL DATABASE
    # ==================================================

    def material_database_habilitada(self):

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = 'material_database_enabled'
            """)

            resultado = cursor.fetchone()

            return (
                resultado is not None
                and resultado[0] == "1"
            )

        finally:

            conexion.close()


    def material_activo_existe(
        self,
        material
    ):

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id
                FROM materials
                WHERE material_number = ?
                  AND active = 1
            """, (
                material,
            ))

            return cursor.fetchone() is not None

        finally:

            conexion.close()


    def validar_material_escaneado(
        self,
        entrada_mat,
        entrada_qty
    ):

        material = (
            entrada_mat
            .get()
            .strip()
        )

        if not material:

            messagebox.showwarning(
                tr(self.idioma, "scan_material_required_title"),
                tr(self.idioma, "scan_material_required")
            )

            entrada_mat.focus_set()
            return "break"

        if (
            self.material_database_habilitada()
            and not self.material_activo_existe(material)
        ):

            messagebox.showwarning(
                tr(self.idioma, "material_not_found_title"),
                tr(
                    self.idioma,
                    "material_not_found",
                    material=material
                )
            )

            entrada_mat.focus_set()
            entrada_mat.selection_range(
                0,
                tk.END
            )

            return "break"

        entrada_qty.focus_set()
        return "break"


    # ==================================================
    # PANTALLA DE CAPTURA
    # ==================================================

    def crear_interfaz(self):

        self.lineas = []

        self.limpiar_ventana()

        self.ventana.geometry("1100x720")

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "pid_title"),
            font=("Arial", 22, "bold")
        ).pack(
            pady=15
        )

        tk.Label(
            self.ventana,
            text=(
                f"{tr(self.idioma, 'user')}: {self.usuario_actual['name']} "
                f"({self.usuario_actual['employee_id']})"
            ),
            font=("Arial", 11)
        ).pack()

        material_mode_key = (
            "material_database_on"
            if self.material_database_habilitada()
            else "material_database_off"
        )

        tk.Label(
            self.ventana,
            text=tr(
                self.idioma,
                material_mode_key
            ),
            font=("Arial", 10, "bold")
        ).pack(
            pady=(3, 0)
        )

        # -----------------------------------
        # DATOS GENERALES
        # -----------------------------------

        datos = tk.LabelFrame(
            self.ventana,
            text=tr(self.idioma, "general_data"),
            padx=15,
            pady=15
        )

        datos.pack(
            fill="x",
            padx=20,
            pady=15
        )

        tk.Label(
            datos,
            text=f"{tr(self.idioma, 'destination')}:"
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        self.destino = ttk.Combobox(
            datos,
            values=self.obtener_destinos(),
            state="readonly",
            width=18
        )

        self.destino.grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Label(
            datos,
            text=f"{tr(self.idioma, 'packaging')}:"
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        self.embalaje = ttk.Combobox(
            datos,
            values=[
                "Pallet",
                "Cajón de madera"
            ],
            state="readonly",
            width=20
        )

        self.embalaje.grid(
            row=0,
            column=3,
            padx=10
        )

        self.embalaje.set("Pallet")

        self.embalaje.bind(
            "<<ComboboxSelected>>",
            self.cambiar_embalaje
        )

        tk.Label(
            datos,
            text=f"{tr(self.idioma, 'total_weight_lb')}:"
        ).grid(
            row=0,
            column=4,
            padx=10
        )

        self.peso = tk.Entry(
            datos,
            width=15
        )

        self.peso.grid(
            row=0,
            column=5,
            padx=10
        )

        # -----------------------------------
        # CONTENIDO DEL PALLET
        # -----------------------------------

        contenido = tk.LabelFrame(
            self.ventana,
            text=tr(self.idioma, "pallet_content"),
            padx=10,
            pady=10
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        encabezados = tk.Frame(
            contenido
        )

        encabezados.pack(
            fill="x"
        )

        tk.Label(
            encabezados,
            text="#",
            width=5
        ).grid(
            row=0,
            column=0
        )

        tk.Label(
            encabezados,
            text="MAT",
            width=25
        ).grid(
            row=0,
            column=1
        )

        tk.Label(
            encabezados,
            text="QTY",
            width=15
        ).grid(
            row=0,
            column=2
        )

        tk.Label(
            encabezados,
            text="WO",
            width=25
        ).grid(
            row=0,
            column=3
        )

        # -----------------------------------
        # ÁREA SCROLL
        # -----------------------------------

        self.canvas = tk.Canvas(
            contenido,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            contenido,
            orient="vertical",
            command=self.canvas.yview
        )

        self.frame_lineas = tk.Frame(
            self.canvas
        )

        self.frame_lineas.bind(
            "<Configure>",
            lambda event:
                self.canvas.configure(
                    scrollregion=
                    self.canvas.bbox("all")
                )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.frame_lineas,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # -----------------------------------
        # BOTONES
        # -----------------------------------

        botones = tk.Frame(
            self.ventana
        )

        botones.pack(
            pady=10
        )

        self.boton_agregar = tk.Button(
            botones,
            text=tr(self.idioma, "add_material"),
            width=18,
            command=self.agregar_linea
        )

        self.boton_agregar.grid(
            row=0,
            column=0,
            padx=5
        )

        self.boton_eliminar = tk.Button(
            botones,
            text=tr(self.idioma, "remove_last_line"),
            width=20,
            command=self.eliminar_linea
        )

        self.boton_eliminar.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "save_pending"),
            width=18,
            command=self.guardar_pendiente
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "print_queue"),
            width=18,
            command=self.mostrar_cola_impresion
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "reprint_last_pid"),
            width=18,
            command=self.reimprimir_ultimo_pid
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        tk.Button(
            self.ventana,
            text=tr(self.idioma, "back_to_menu"),
            width=20,
            command=self.volver_menu
        ).pack(
            pady=10
        )

        self.agregar_linea()


    # ==================================================
    # LÍNEAS MAT / QTY / WO
    # ==================================================

    def agregar_linea(self):

        if (
            self.embalaje.get() == "Cajón de madera"
            and len(self.lineas) >= 1
        ):

            return

        numero = len(self.lineas) + 1

        fila = tk.Frame(
            self.frame_lineas
        )

        fila.pack(
            pady=3
        )

        tk.Label(
            fila,
            text=str(numero),
            width=5
        ).grid(
            row=0,
            column=0
        )

        entrada_mat = tk.Entry(
            fila,
            width=25
        )

        entrada_mat.grid(
            row=0,
            column=1,
            padx=5
        )

        entrada_qty = tk.Entry(
            fila,
            width=15
        )

        entrada_qty.grid(
            row=0,
            column=2,
            padx=5
        )

        entrada_wo = tk.Entry(
            fila,
            width=25
        )

        entrada_wo.grid(
            row=0,
            column=3,
            padx=5
        )

        # Scanner:
        # MAT -> QTY -> WO -> siguiente línea

        entrada_mat.bind(
            "<Return>",
            lambda event:
                self.validar_material_escaneado(
                    entrada_mat,
                    entrada_qty
                )
        )

        entrada_qty.bind(
            "<Return>",
            lambda event:
                entrada_wo.focus_set()
        )

        entrada_wo.bind(
            "<Return>",
            lambda event:
                self.finalizar_linea()
        )

        self.lineas.append({
            "frame": fila,
            "mat": entrada_mat,
            "qty": entrada_qty,
            "wo": entrada_wo
        })

        entrada_mat.focus_set()

        self.canvas.update_idletasks()

        self.canvas.yview_moveto(
            1.0
        )


    def finalizar_linea(self):

        if self.embalaje.get() == "Pallet":

            self.agregar_linea()

        else:

            self.peso.focus_set()


    def eliminar_linea(self):

        if len(self.lineas) <= 1:
            return

        ultima = self.lineas.pop()

        ultima["frame"].destroy()

        self.lineas[-1][
            "mat"
        ].focus_set()


    def cambiar_embalaje(
        self,
        event=None
    ):

        if self.embalaje.get() == "Cajón de madera":

            if len(self.lineas) > 1:

                messagebox.showwarning(
                    tr(self.idioma, "not_allowed_title"),
                    tr(self.idioma, "wooden_box_one_material")
                )

                self.embalaje.set(
                    "Pallet"
                )

                return

            self.boton_agregar.config(
                state="disabled"
            )

            self.boton_eliminar.config(
                state="disabled"
            )

        else:

            self.boton_agregar.config(
                state="normal"
            )

            self.boton_eliminar.config(
                state="normal"
            )


    # ==================================================
    # VALIDAR CAPTURA
    # ==================================================

    def obtener_datos_captura(self):

        destino = self.destino.get()

        embalaje = self.embalaje.get()

        if not destino:

            messagebox.showwarning(
                tr(self.idioma, "destination_required_title"),
                tr(self.idioma, "destination_required")
            )

            return None

        try:

            peso = float(
                self.peso.get()
            )

            if (
                not math.isfinite(peso)
                or peso <= 0
            ):

                raise ValueError

        except ValueError:

            messagebox.showwarning(
                tr(self.idioma, "invalid_weight_title"),
                tr(self.idioma, "invalid_weight")
            )

            return None

        materiales = []

        for numero, linea in enumerate(
            self.lineas,
            start=1
        ):

            mat = (
                linea["mat"]
                .get()
                .strip()
            )

            qty = (
                linea["qty"]
                .get()
                .strip()
            )

            wo = (
                linea["wo"]
                .get()
                .strip()
            )

            # Ignorar línea totalmente vacía

            if (
                not mat
                and not qty
                and not wo
            ):

                continue

            if (
                not mat
                or not qty
                or not wo
            ):

                messagebox.showwarning(
                    tr(self.idioma, "incomplete_line_title"),
                    tr(
                        self.idioma,
                        "incomplete_line",
                        line=numero
                    )
                )

                return None

            if (
                self.material_database_habilitada()
                and not self.material_activo_existe(mat)
            ):

                messagebox.showwarning(
                    tr(self.idioma, "material_not_found_title"),
                    tr(
                        self.idioma,
                        "material_not_found",
                        material=mat
                    )
                )

                linea["mat"].focus_set()
                linea["mat"].selection_range(
                    0,
                    tk.END
                )

                return None

            try:

                cantidad = float(
                    qty
                )

                if (
                    not math.isfinite(cantidad)
                    or cantidad <= 0
                ):

                    raise ValueError

            except ValueError:

                messagebox.showwarning(
                    tr(self.idioma, "invalid_quantity_title"),
                    tr(
                        self.idioma,
                        "invalid_quantity",
                        line=numero
                    )
                )

                return None

            materiales.append({
                "material": mat,
                "quantity": cantidad,
                "work_order": wo
            })

        if not materiales:

            messagebox.showwarning(
                tr(self.idioma, "no_materials_title"),
                tr(self.idioma, "no_materials")
            )

            return None

        if (
            embalaje == "Cajón de madera"
            and len(materiales) != 1
        ):

            messagebox.showwarning(
                tr(self.idioma, "not_allowed_title"),
                tr(self.idioma, "wooden_box_one_material")
            )

            return None

        return {
            "destination": destino,
            "packaging": embalaje,
            "weight": peso,
            "items": materiales
        }


    # ==================================================
    # GUARDAR PENDING
    # ==================================================

    def guardar_pendiente(self):

        datos = self.obtener_datos_captura()

        if datos is None:
            return

        confirmar = messagebox.askyesno(
            tr(self.idioma, "save_pending_title"),
            tr(
                self.idioma,
                "save_pending_confirm",
                destination=datos["destination"],
                packaging=datos["packaging"],
                weight=datos["weight"],
                materials=len(datos["items"])
            )
        )

        if not confirmar:
            return

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id
                FROM destinations
                WHERE code = ?
                  AND active = 1
            """, (
                datos["destination"],
            ))

            resultado = cursor.fetchone()

            if resultado is None:

                raise ValueError(
                    "Destination not found."
                )

            destination_id = resultado[0]

            fecha = (
                datetime
                .now()
                .astimezone()
                .isoformat(
                    timespec="seconds"
                )
            )

            cursor.execute("""
                INSERT INTO pallets (
                    pallet_id,
                    user_id,
                    destination_id,
                    packaging_type,
                    weight_lb,
                    status,
                    created_at,
                    printed_at,
                    qr_data
                )
                VALUES (
                    NULL,
                    ?, ?, ?, ?,
                    'PENDING',
                    ?,
                    NULL,
                    NULL
                )
            """, (
                self.usuario_actual["id"],
                destination_id,
                datos["packaging"],
                datos["weight"],
                fecha
            ))

            pallet_record_id = (
                cursor.lastrowid
            )

            for numero, item in enumerate(
                datos["items"],
                start=1
            ):

                cursor.execute("""
                    INSERT INTO pallet_items (
                        pallet_record_id,
                        line_no,
                        material,
                        quantity,
                        work_order
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pallet_record_id,
                    numero,
                    item["material"],
                    item["quantity"],
                    item["work_order"]
                ))

            conexion.commit()

        except Exception as error:

            conexion.rollback()

            messagebox.showerror(
                tr(self.idioma, "save_error_title"),
                tr(
                    self.idioma,
                    "save_error",
                    error=error
                )
            )

            return

        finally:

            conexion.close()

        messagebox.showinfo(
            tr(self.idioma, "pending_saved_title"),
            tr(
                self.idioma,
                "pending_saved",
                record=pallet_record_id
            )
        )

        self.mostrar_cola_impresion()


    # ==================================================
    # COLA DE IMPRESIÓN
    # ==================================================

    def mostrar_cola_impresion(self):

        self.limpiar_ventana()

        self.ventana.geometry(
            "1000x620"
        )

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "pid_print_queue"),
            font=("Arial", 22, "bold")
        ).pack(
            pady=20
        )

        tk.Label(
            self.ventana,
            text=tr(
                self.idioma,
                "select_pending_instruction"
            ),
            font=("Arial", 11)
        ).pack(
            pady=5
        )

        frame = tk.Frame(
            self.ventana
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        columnas = (
            "record",
            "destination",
            "packaging",
            "weight",
            "created"
        )

        self.tabla_pendientes = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=15
        )

        self.tabla_pendientes.heading(
            "record",
            text=tr(self.idioma, "record")
        )

        self.tabla_pendientes.heading(
            "destination",
            text=tr(self.idioma, "destination")
        )

        self.tabla_pendientes.heading(
            "packaging",
            text=tr(self.idioma, "packaging")
        )

        self.tabla_pendientes.heading(
            "weight",
            text=tr(self.idioma, "weight_lb")
        )

        self.tabla_pendientes.heading(
            "created",
            text=tr(self.idioma, "created")
        )

        self.tabla_pendientes.column(
            "record",
            width=80
        )

        self.tabla_pendientes.column(
            "destination",
            width=120
        )

        self.tabla_pendientes.column(
            "packaging",
            width=180
        )

        self.tabla_pendientes.column(
            "weight",
            width=100
        )

        self.tabla_pendientes.column(
            "created",
            width=250
        )

        self.tabla_pendientes.pack(
            fill="both",
            expand=True
        )

        botones = tk.Frame(
            self.ventana
        )

        botones.pack(
            pady=15
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "print_selected"),
            width=20,
            command=self.imprimir_seleccionado
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "refresh"),
            width=15,
            command=self.cargar_pendientes
        ).grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "reprint_last_pid"),
            width=20,
            command=self.reimprimir_ultimo_pid
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        tk.Button(
            botones,
            text=tr(self.idioma, "new_capture"),
            width=15,
            command=self.crear_interfaz
        ).grid(
            row=0,
            column=3,
            padx=10
        )

        tk.Button(
            self.ventana,
            text=tr(self.idioma, "back_to_menu"),
            width=20,
            command=self.volver_menu
        ).pack(
            pady=10
        )

        self.cargar_pendientes()


    def cargar_pendientes(self):

        for item in (
            self.tabla_pendientes
            .get_children()
        ):

            self.tabla_pendientes.delete(
                item
            )

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                pallets.id,
                destinations.code,
                pallets.packaging_type,
                pallets.weight_lb,
                pallets.created_at
            FROM pallets

            INNER JOIN destinations
                ON destinations.id =
                   pallets.destination_id

            WHERE pallets.status = 'PENDING'

            ORDER BY pallets.id
        """)

        registros = (
            cursor.fetchall()
        )

        conexion.close()

        for registro in registros:

            self.tabla_pendientes.insert(
                "",
                tk.END,
                values=registro
            )


    # ==================================================
    # GENERAR PID
    # ==================================================

    def generar_pid_para_pallet(
        self,
        pallet_record_id
    ):

        ahora = (
            datetime
            .now()
            .astimezone()
        )

        # MMDDYY

        date_code = (
            ahora.strftime(
                "%m%d%y"
            )
        )

        printed_at = (
            ahora.isoformat(
                timespec="seconds"
            )
        )

        conexion = conectar()

        try:

            conexion.execute(
                "BEGIN IMMEDIATE"
            )

            cursor = conexion.cursor()

            # -----------------------------------
            # DIVISIÓN
            # -----------------------------------

            cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = 'division_code'
            """)

            resultado = (
                cursor.fetchone()
            )

            if (
                resultado is None
                or not resultado[0]
            ):

                raise ValueError(
                    "PID division is not configured."
                )

            division = (
                resultado[0]
                .strip()
                .upper()
            )

            # -----------------------------------
            # PALLET
            # -----------------------------------

            cursor.execute("""
                SELECT
                    pallets.id,
                    pallets.status,
                    pallets.pallet_id,
                    pallets.packaging_type,
                    pallets.weight_lb,
                    destinations.code,
                    users.employee_id
                FROM pallets

                INNER JOIN destinations
                    ON destinations.id =
                       pallets.destination_id

                INNER JOIN users
                    ON users.id =
                       pallets.user_id

                WHERE pallets.id = ?
            """, (
                pallet_record_id,
            ))

            pallet = (
                cursor.fetchone()
            )

            if pallet is None:

                raise ValueError(
                    "Pallet not found."
                )

            if pallet[1] != "PENDING":

                raise ValueError(
                    "This pallet is no longer pending."
                )

            if pallet[2] is not None:

                raise ValueError(
                    "This pallet already has a PID."
                )

            packaging = pallet[3]
            weight = pallet[4]
            destination = pallet[5]
            employee_id = pallet[6]

            # -----------------------------------
            # CONSECUTIVO
            # -----------------------------------

            cursor.execute("""
                SELECT last_number
                FROM pid_sequences
                WHERE date_code = ?
                  AND division_code = ?
            """, (
                date_code,
                division
            ))

            secuencia = (
                cursor.fetchone()
            )

            if secuencia is None:

                numero = 1

                cursor.execute("""
                    INSERT INTO pid_sequences (
                        date_code,
                        division_code,
                        last_number
                    )
                    VALUES (?, ?, ?)
                """, (
                    date_code,
                    division,
                    numero
                ))

            else:

                anterior = (
                    secuencia[0]
                )

                if anterior >= 9999:

                    numero = 1

                else:

                    numero = (
                        anterior + 1
                    )

                cursor.execute("""
                    UPDATE pid_sequences
                    SET last_number = ?
                    WHERE date_code = ?
                      AND division_code = ?
                """, (
                    numero,
                    date_code,
                    division
                ))

            pid = (
                f"{date_code}-"
                f"{division}-"
                f"{numero:04d}"
            )

            # Protección contra duplicado

            cursor.execute("""
                SELECT id
                FROM pallets
                WHERE pallet_id = ?
            """, (
                pid,
            ))

            if (
                cursor.fetchone()
                is not None
            ):

                raise ValueError(
                    (
                        f"PID {pid} already exists. "
                        "Printing was cancelled."
                    )
                )

            # -----------------------------------
            # MATERIALES
            # -----------------------------------

            cursor.execute("""
                SELECT
                    material,
                    quantity,
                    work_order
                FROM pallet_items

                WHERE pallet_record_id = ?

                ORDER BY line_no
            """, (
                pallet_record_id,
            ))

            items_db = (
                cursor.fetchall()
            )

            if not items_db:

                raise ValueError(
                    "The pallet has no materials."
                )

            items = []

            for (
                material,
                quantity,
                wo
            ) in items_db:

                items.append({
                    "material": material,
                    "quantity": quantity,
                    "work_order": wo
                })

            # -----------------------------------
            # CONTENIDO QR
            # -----------------------------------

            contenido_qr = {
                "version": 1,
                "pid": pid,
                "destination":
                    destination,
                "packaging":
                    packaging,
                "weight_lb":
                    weight,
                "employee_id":
                    employee_id,
                "items":
                    items
            }

            qr_data = json.dumps(
                contenido_qr,
                ensure_ascii=False,
                separators=(",", ":")
            )

            # -----------------------------------
            # ACTUALIZAR PALLET
            # -----------------------------------

            cursor.execute("""
                UPDATE pallets

                SET
                    pallet_id = ?,
                    status = 'PRINTED',
                    printed_at = ?,
                    qr_data = ?

                WHERE id = ?
            """, (
                pid,
                printed_at,
                qr_data,
                pallet_record_id
            ))

            # -----------------------------------
            # HISTORIAL
            # -----------------------------------

            cursor.execute("""
                INSERT INTO print_history (
                    pallet_record_id,
                    printed_by,
                    printed_at,
                    is_reprint
                )
                VALUES (?, ?, ?, 0)
            """, (
                pallet_record_id,
                self.usuario_actual["id"],
                printed_at
            ))

            conexion.commit()

        except Exception:

            conexion.rollback()

            raise

        finally:

            conexion.close()

        return (
            pid,
            qr_data
        )


    # ==================================================
    # PRINT SELECTED
    # ==================================================

    def imprimir_seleccionado(self):

        seleccion = (
            self.tabla_pendientes
            .selection()
        )

        if not seleccion:

            messagebox.showwarning(
                tr(self.idioma, "select_pallet_title"),
                tr(self.idioma, "select_pallet_message")
            )

            return

        valores = (
            self.tabla_pendientes
            .item(
                seleccion[0],
                "values"
            )
        )

        pallet_record_id = int(
            valores[0]
        )

        confirmar = (
            messagebox.askyesno(
                tr(self.idioma, "print_pid_title"),
                tr(
                    self.idioma,
                    "print_pid_confirm",
                    record=pallet_record_id,
                    destination=valores[1],
                    weight=valores[3]
                )
            )
        )

        if not confirmar:
            return

        # -----------------------------------
        # GENERAR PID
        # -----------------------------------

        try:

            pid, qr_data = (
                self.generar_pid_para_pallet(
                    pallet_record_id
                )
            )

        except Exception as error:

            messagebox.showerror(
                tr(self.idioma, "pid_error_title"),
                tr(
                    self.idioma,
                    "pid_error",
                    error=error
                )
            )

            return

        # -----------------------------------
        # GENERAR QR Y ETIQUETA
        # -----------------------------------

        try:

            ruta_qr = generar_qr(
                pid,
                qr_data
            )

            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT
                    destinations.code,
                    pallets.packaging_type,
                    pallets.weight_lb,
                    users.employee_id
                FROM pallets

                INNER JOIN destinations
                    ON destinations.id =
                       pallets.destination_id

                INNER JOIN users
                    ON users.id =
                       pallets.user_id

                WHERE pallets.id = ?
            """, (
                pallet_record_id,
            ))

            datos_etiqueta = (
                cursor.fetchone()
            )

            conexion.close()

            if datos_etiqueta is None:

                raise ValueError(
                    "Label information "
                    "could not be found."
                )

            destination = (
                datos_etiqueta[0]
            )

            packaging = (
                datos_etiqueta[1]
            )

            weight_lb = (
                datos_etiqueta[2]
            )

            employee_id = (
                datos_etiqueta[3]
            )

            ruta_etiqueta = (
                generar_etiqueta(
                    pid,
                    destination,
                    packaging,
                    weight_lb,
                    employee_id
                )
            )

        except Exception as error:

            messagebox.showwarning(
                tr(self.idioma, "label_problem_title"),
                tr(
                    self.idioma,
                    "label_problem",
                    pid=pid,
                    error=error
                )
            )

            self.cargar_pendientes()

            return

        # -----------------------------------
        # RESULTADO
        # -----------------------------------

        messagebox.showinfo(
            tr(self.idioma, "pid_created_title"),
            tr(
                self.idioma,
                "pid_created",
                pid=pid,
                qr=ruta_qr,
                label=ruta_etiqueta
            )
        )

        self.cargar_pendientes()


    # ==================================================
    # REPRINT LAST PID
    # ==================================================

    def reimprimir_ultimo_pid(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                pallets.id,
                pallets.pallet_id,
                pallets.qr_data,
                destinations.code,
                pallets.packaging_type,
                pallets.weight_lb,
                users.employee_id
            FROM pallets

            INNER JOIN destinations
                ON destinations.id =
                   pallets.destination_id

            INNER JOIN users
                ON users.id =
                   pallets.user_id

            WHERE pallets.status = 'PRINTED'
              AND pallets.pallet_id IS NOT NULL

            ORDER BY
                pallets.printed_at DESC,
                pallets.id DESC

            LIMIT 1
        """)

        resultado = (
            cursor.fetchone()
        )

        conexion.close()

        if resultado is None:

            messagebox.showwarning(
                tr(self.idioma, "no_pid_title"),
                tr(self.idioma, "no_pid_message")
            )

            return

        pallet_record_id = resultado[0]
        pid = resultado[1]
        qr_data = resultado[2]

        destination = resultado[3]
        packaging = resultado[4]
        weight_lb = resultado[5]
        employee_id = resultado[6]

        confirmar = (
            messagebox.askyesno(
                tr(self.idioma, "confirm_reprint_title"),
                tr(
                    self.idioma,
                    "confirm_reprint",
                    pid=pid
                )
            )
        )

        if not confirmar:
            return

        try:

            # Regenerar QR

            ruta_qr = generar_qr(
                pid,
                qr_data
            )

            # Regenerar etiqueta 4x2

            ruta_etiqueta = (
                generar_etiqueta(
                    pid,
                    destination,
                    packaging,
                    weight_lb,
                    employee_id
                )
            )

            # Registrar reimpresión

            fecha = (
                datetime
                .now()
                .astimezone()
                .isoformat(
                    timespec="seconds"
                )
            )

            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO print_history (
                    pallet_record_id,
                    printed_by,
                    printed_at,
                    is_reprint
                )
                VALUES (?, ?, ?, 1)
            """, (
                pallet_record_id,
                self.usuario_actual["id"],
                fecha
            ))

            conexion.commit()
            conexion.close()

        except Exception as error:

            messagebox.showerror(
                tr(self.idioma, "reprint_error_title"),
                tr(
                    self.idioma,
                    "reprint_error",
                    error=error
                )
            )

            return

        messagebox.showinfo(
            tr(self.idioma, "reprint_ready_title"),
            tr(
                self.idioma,
                "reprint_ready",
                pid=pid,
                qr=ruta_qr,
                label=ruta_etiqueta
            )
        )