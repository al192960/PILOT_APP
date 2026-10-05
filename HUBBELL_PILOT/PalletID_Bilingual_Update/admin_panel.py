import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from database import (
    conectar,
    obtener_configuracion,
    guardar_configuracion,
    agregar_o_actualizar_material,
    desactivar_material
)

from auth import generar_hash
from material_importer import importar_materiales
from translations import tr


class AdminPanel:

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

        self.crear_interfaz()


    # ==================================================
    # UTILIDADES
    # ==================================================

    def limpiar_ventana(self):

        for widget in self.ventana.winfo_children():
            widget.destroy()


    # ==================================================
    # INTERFAZ
    # ==================================================

    def crear_interfaz(self):

        self.limpiar_ventana()

        self.ventana.geometry("1050x760")

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "admin_title"),
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        tk.Label(
            self.ventana,
            text=(
                f"{tr(self.idioma, 'administrator')}: "
                f"{self.usuario_actual['name']}"
            ),
            font=("Arial", 11)
        ).pack()

        notebook = ttk.Notebook(
            self.ventana
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # ==============================================
        # TAB 1 - GENERAL
        # ==============================================

        tab_general = tk.Frame(
            notebook
        )

        notebook.add(
            tab_general,
            text=tr(self.idioma, "general")
        )

        self.crear_tab_general(
            tab_general
        )

        # ==============================================
        # TAB 2 - USERS
        # ==============================================

        tab_users = tk.Frame(
            notebook
        )

        notebook.add(
            tab_users,
            text=tr(self.idioma, "users")
        )

        self.crear_tab_users(
            tab_users
        )

        # ==============================================
        # TAB 3 - MATERIAL DATABASE
        # ==============================================

        tab_materials = tk.Frame(
            notebook
        )

        notebook.add(
            tab_materials,
            text=tr(self.idioma, "material_database_tab")
        )

        self.crear_tab_materials(
            tab_materials
        )

        # ==============================================
        # VOLVER
        # ==============================================

        tk.Button(
            self.ventana,
            text=tr(self.idioma, "back_to_menu"),
            width=22,
            command=self.volver_menu
        ).pack(pady=10)


    # ==================================================
    # TAB GENERAL
    # ==================================================

    def crear_tab_general(
        self,
        parent
    ):

        frame_division = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "pid_division"),
            padx=15,
            pady=15
        )

        frame_division.pack(
            fill="x",
            padx=20,
            pady=20
        )

        tk.Label(
            frame_division,
            text=f"{tr(self.idioma, 'current_division')}:"
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        self.entrada_division = tk.Entry(
            frame_division,
            width=15,
            font=("Arial", 12),
            justify="center"
        )

        self.entrada_division.grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Button(
            frame_division,
            text=tr(self.idioma, "save_division"),
            command=self.guardar_division
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        self.cargar_division()


    def cargar_division(self):

        division = obtener_configuracion(
            "division_code"
        )

        self.entrada_division.delete(
            0,
            tk.END
        )

        if division:

            self.entrada_division.insert(
                0,
                division
            )


    def guardar_division(self):

        division = (
            self.entrada_division
            .get()
            .strip()
            .upper()
        )

        if not division:

            messagebox.showwarning(
                tr(self.idioma, "invalid_division_title"),
                tr(self.idioma, "enter_division")
            )

            return

        if len(division) > 10:

            messagebox.showwarning(
                tr(self.idioma, "invalid_division_title"),
                tr(self.idioma, "division_too_long")
            )

            return

        guardar_configuracion(
            "division_code",
            division
        )

        self.cargar_division()

        messagebox.showinfo(
            tr(self.idioma, "division_saved_title"),
            tr(
                self.idioma,
                "division_saved",
                division=division
            )
        )


    # ==================================================
    # TAB USERS
    # ==================================================

    def crear_tab_users(
        self,
        parent
    ):

        frame_usuario = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "create_user"),
            padx=15,
            pady=15
        )

        frame_usuario.pack(
            fill="x",
            padx=20,
            pady=15
        )

        tk.Label(
            frame_usuario,
            text=tr(self.idioma, "employee_id")
        ).grid(
            row=0,
            column=0,
            padx=8,
            pady=5
        )

        self.employee_id = tk.Entry(
            frame_usuario,
            width=18
        )

        self.employee_id.grid(
            row=0,
            column=1,
            padx=8
        )

        tk.Label(
            frame_usuario,
            text=tr(self.idioma, "name")
        ).grid(
            row=0,
            column=2,
            padx=8
        )

        self.nombre = tk.Entry(
            frame_usuario,
            width=25
        )

        self.nombre.grid(
            row=0,
            column=3,
            padx=8
        )

        tk.Label(
            frame_usuario,
            text=tr(self.idioma, "password")
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=10
        )

        self.password = tk.Entry(
            frame_usuario,
            width=18,
            show="*"
        )

        self.password.grid(
            row=1,
            column=1,
            padx=8
        )

        tk.Label(
            frame_usuario,
            text=tr(self.idioma, "role")
        ).grid(
            row=1,
            column=2,
            padx=8
        )

        self.role = ttk.Combobox(
            frame_usuario,
            values=[
                "USER",
                "GROUP_LEADER",
                "ADMIN"
            ],
            state="readonly",
            width=20
        )

        self.role.grid(
            row=1,
            column=3,
            padx=8
        )

        self.role.set(
            "USER"
        )

        self.packing_permission = (
            tk.IntVar(
                value=0
            )
        )

        tk.Checkbutton(
            frame_usuario,
            text=tr(self.idioma, "allow_packing_list"),
            variable=self.packing_permission
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=10
        )

        tk.Button(
            frame_usuario,
            text=tr(self.idioma, "create_user_button"),
            width=20,
            command=self.crear_usuario
        ).grid(
            row=2,
            column=3,
            pady=10
        )

        # -----------------------------------
        # LISTA USERS
        # -----------------------------------

        frame_lista = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "users"),
            padx=10,
            pady=10
        )

        frame_lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columnas = (
            "employee_id",
            "name",
            "role",
            "packing",
            "active"
        )

        self.tabla_users = ttk.Treeview(
            frame_lista,
            columns=columnas,
            show="headings",
            height=12
        )

        self.tabla_users.heading(
            "employee_id",
            text=tr(self.idioma, "employee_id")
        )

        self.tabla_users.heading(
            "name",
            text=tr(self.idioma, "name")
        )

        self.tabla_users.heading(
            "role",
            text=tr(self.idioma, "role")
        )

        self.tabla_users.heading(
            "packing",
            text=tr(self.idioma, "packing_list")
        )

        self.tabla_users.heading(
            "active",
            text=tr(self.idioma, "active")
        )

        self.tabla_users.column(
            "employee_id",
            width=120
        )

        self.tabla_users.column(
            "name",
            width=220
        )

        self.tabla_users.column(
            "role",
            width=130
        )

        self.tabla_users.column(
            "packing",
            width=100
        )

        self.tabla_users.column(
            "active",
            width=80
        )

        self.tabla_users.pack(
            fill="both",
            expand=True
        )

        self.cargar_usuarios()


    def crear_usuario(self):

        employee_id = (
            self.employee_id
            .get()
            .strip()
        )

        nombre = (
            self.nombre
            .get()
            .strip()
        )

        password = (
            self.password
            .get()
        )

        role = (
            self.role.get()
        )

        packing = (
            self.packing_permission
            .get()
        )

        if (
            not employee_id
            or not nombre
            or not password
        ):

            messagebox.showwarning(
                tr(self.idioma, "required_fields_title"),
                tr(self.idioma, "required_user_fields")
            )

            return

        if role in (
            "ADMIN",
            "GROUP_LEADER"
        ):

            packing = 1

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id
            FROM users
            WHERE employee_id = ?
        """, (
            employee_id,
        ))

        if cursor.fetchone() is not None:

            conexion.close()

            messagebox.showerror(
                tr(self.idioma, "user_exists_title"),
                tr(self.idioma, "user_exists")
            )

            return

        password_hash = (
            generar_hash(
                password
            )
        )

        fecha = (
            datetime
            .now()
            .astimezone()
            .isoformat(
                timespec="seconds"
            )
        )

        cursor.execute("""
            INSERT INTO users (
                employee_id,
                name,
                password_hash,
                role,
                can_create_packing_list,
                active,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            nombre,
            password_hash,
            role,
            packing,
            1,
            fecha
        ))

        conexion.commit()
        conexion.close()

        messagebox.showinfo(
            tr(self.idioma, "user_created_title"),
            tr(self.idioma, "user_created")
        )

        self.employee_id.delete(
            0,
            tk.END
        )

        self.nombre.delete(
            0,
            tk.END
        )

        self.password.delete(
            0,
            tk.END
        )

        self.role.set(
            "USER"
        )

        self.packing_permission.set(
            0
        )

        self.cargar_usuarios()


    def cargar_usuarios(self):

        for item in (
            self.tabla_users
            .get_children()
        ):

            self.tabla_users.delete(
                item
            )

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                employee_id,
                name,
                role,
                can_create_packing_list,
                active
            FROM users
            ORDER BY name
        """)

        usuarios = cursor.fetchall()

        conexion.close()

        for usuario in usuarios:

            packing = (
                tr(self.idioma, "yes")
                if usuario[3] == 1
                else tr(self.idioma, "no")
            )

            active = (
                tr(self.idioma, "yes")
                if usuario[4] == 1
                else tr(self.idioma, "no")
            )

            self.tabla_users.insert(
                "",
                tk.END,
                values=(
                    usuario[0],
                    usuario[1],
                    usuario[2],
                    packing,
                    active
                )
            )


    # ==================================================
    # TAB MATERIAL DATABASE
    # ==================================================

    def crear_tab_materials(
        self,
        parent
    ):

        # -----------------------------------
        # MODO ON / OFF
        # -----------------------------------

        frame_mode = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "material_database_mode"),
            padx=15,
            pady=15
        )

        frame_mode.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.material_mode_label = tk.Label(
            frame_mode,
            font=("Arial", 12, "bold")
        )

        self.material_mode_label.grid(
            row=0,
            column=0,
            padx=10
        )

        self.boton_material_mode = tk.Button(
            frame_mode,
            width=20,
            command=self.cambiar_material_mode
        )

        self.boton_material_mode.grid(
            row=0,
            column=1,
            padx=15
        )

        self.actualizar_material_mode_ui()

        # -----------------------------------
        # ALTA / UPDATE MANUAL
        # -----------------------------------

        frame_edit = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "add_update_material"),
            padx=15,
            pady=15
        )

        frame_edit.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            frame_edit,
            text=f"{tr(self.idioma, 'material')}:"
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        self.material_number = tk.Entry(
            frame_edit,
            width=22
        )

        self.material_number.grid(
            row=0,
            column=1,
            padx=8
        )

        tk.Label(
            frame_edit,
            text=f"{tr(self.idioma, 'description')}:"
        ).grid(
            row=0,
            column=2,
            padx=8
        )

        self.material_description = tk.Entry(
            frame_edit,
            width=35
        )

        self.material_description.grid(
            row=0,
            column=3,
            padx=8
        )

        tk.Button(
            frame_edit,
            text=tr(self.idioma, "add_update"),
            width=18,
            command=self.guardar_material_manual
        ).grid(
            row=0,
            column=4,
            padx=10
        )

        # -----------------------------------
        # BÚSQUEDA
        # -----------------------------------

        frame_search = tk.Frame(
            parent
        )

        frame_search.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            frame_search,
            text=f"{tr(self.idioma, 'search_material')}:"
        ).pack(
            side="left"
        )

        self.material_search = tk.Entry(
            frame_search,
            width=25
        )

        self.material_search.pack(
            side="left",
            padx=10
        )

        self.material_search.bind(
            "<KeyRelease>",
            lambda event:
                self.cargar_materiales()
        )

        tk.Button(
            frame_search,
            text=tr(self.idioma, "clear"),
            command=self.limpiar_busqueda_material
        ).pack(
            side="left"
        )

        # -----------------------------------
        # TABLA MATERIALS
        # -----------------------------------

        frame_table = tk.LabelFrame(
            parent,
            text=tr(self.idioma, "materials"),
            padx=10,
            pady=10
        )

        frame_table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        columnas = (
            "material",
            "description",
            "active",
            "updated"
        )

        self.tabla_materiales = ttk.Treeview(
            frame_table,
            columns=columnas,
            show="headings",
            height=9
        )

        self.tabla_materiales.heading(
            "material",
            text=tr(self.idioma, "material")
        )

        self.tabla_materiales.heading(
            "description",
            text=tr(self.idioma, "description")
        )

        self.tabla_materiales.heading(
            "active",
            text=tr(self.idioma, "active")
        )

        self.tabla_materiales.heading(
            "updated",
            text=tr(self.idioma, "updated")
        )

        self.tabla_materiales.column(
            "material",
            width=160
        )

        self.tabla_materiales.column(
            "description",
            width=320
        )

        self.tabla_materiales.column(
            "active",
            width=80
        )

        self.tabla_materiales.column(
            "updated",
            width=220
        )

        self.tabla_materiales.pack(
            fill="both",
            expand=True
        )

        # -----------------------------------
        # BOTONES MATERIAL
        # -----------------------------------

        frame_buttons = tk.Frame(
            parent
        )

        frame_buttons.pack(
            pady=5
        )

        tk.Button(
            frame_buttons,
            text=tr(self.idioma, "load_selected"),
            width=18,
            command=self.cargar_material_seleccionado
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        tk.Button(
            frame_buttons,
            text=tr(self.idioma, "deactivate_selected"),
            width=22,
            command=self.desactivar_material_seleccionado
        ).grid(
            row=0,
            column=1,
            padx=8
        )

        tk.Button(
            frame_buttons,
            text=tr(self.idioma, "refresh"),
            width=15,
            command=self.cargar_materiales
        ).grid(
            row=0,
            column=2,
            padx=8
        )

        tk.Button(
            frame_buttons,
            text=tr(self.idioma, "import_xlsx"),
            width=18,
            command=self.importar_xlsx
            ).grid(
            row=0,
            column=3,
            padx=8
)
        self.cargar_materiales()


    # ==================================================
    # MATERIAL DATABASE MODE
    # ==================================================

    def actualizar_material_mode_ui(self):

        valor = obtener_configuracion(
            "material_database_enabled"
        )

        habilitado = (
            valor == "1"
        )

        if habilitado:

            self.material_mode_label.config(
                text=(
                    f"{tr(self.idioma, 'status')}: "
                    f"{tr(self.idioma, 'on')}"
                )
            )

            self.boton_material_mode.config(
                text=tr(self.idioma, "turn_off")
            )

        else:

            self.material_mode_label.config(
                text=(
                    f"{tr(self.idioma, 'status')}: "
                    f"{tr(self.idioma, 'off')}"
                )
            )

            self.boton_material_mode.config(
                text=tr(self.idioma, "turn_on")
            )


    def cambiar_material_mode(self):

        actual = obtener_configuracion(
            "material_database_enabled"
        )

        nuevo = (
            "0"
            if actual == "1"
            else "1"
        )

        texto = (
            tr(self.idioma, "enable")
            if nuevo == "1"
            else tr(self.idioma, "disable")
        )

        confirmar = messagebox.askyesno(
            tr(self.idioma, "material_database_mode"),
            tr(
                self.idioma,
                "material_mode_confirm",
                action=texto
            )
        )

        if not confirmar:
            return

        guardar_configuracion(
            "material_database_enabled",
            nuevo
        )

        self.actualizar_material_mode_ui()


    # ==================================================
    # MATERIALS
    # ==================================================

    def guardar_material_manual(self):

        material = (
            self.material_number
            .get()
            .strip()
        )

        descripcion = (
            self.material_description
            .get()
            .strip()
        )

        if not material:

            messagebox.showwarning(
                tr(self.idioma, "material_required_title"),
                tr(self.idioma, "material_required")
            )

            return

        try:

            agregar_o_actualizar_material(
                material,
                descripcion
            )

        except Exception as error:

            messagebox.showerror(
                tr(self.idioma, "material_error_title"),
                str(error)
            )

            return

        messagebox.showinfo(
            tr(self.idioma, "material_saved_title"),
            tr(
                self.idioma,
                "material_saved",
                material=material
            )
        )

        self.material_number.delete(
            0,
            tk.END
        )

        self.material_description.delete(
            0,
            tk.END
        )

        self.cargar_materiales()


    def cargar_materiales(self):

        if not hasattr(
            self,
            "tabla_materiales"
        ):
            return

        for item in (
            self.tabla_materiales
            .get_children()
        ):

            self.tabla_materiales.delete(
                item
            )

        busqueda = ""

        if hasattr(
            self,
            "material_search"
        ):

            busqueda = (
                self.material_search
                .get()
                .strip()
            )

        conexion = conectar()
        cursor = conexion.cursor()

        if busqueda:

            cursor.execute("""
                SELECT
                    material_number,
                    description,
                    active,
                    updated_at
                FROM materials

                WHERE material_number
                    LIKE ?

                ORDER BY material_number
            """, (
                f"%{busqueda}%",
            ))

        else:

            cursor.execute("""
                SELECT
                    material_number,
                    description,
                    active,
                    updated_at
                FROM materials

                ORDER BY material_number
            """)

        registros = cursor.fetchall()

        conexion.close()

        for registro in registros:

            active = (
                tr(self.idioma, "yes")
                if registro[2] == 1
                else tr(self.idioma, "no")
            )

            self.tabla_materiales.insert(
                "",
                tk.END,
                values=(
                    registro[0],
                    registro[1] or "",
                    active,
                    registro[3]
                )
            )


    def cargar_material_seleccionado(self):

        seleccion = (
            self.tabla_materiales
            .selection()
        )

        if not seleccion:

            messagebox.showwarning(
                tr(self.idioma, "select_material_title"),
                tr(self.idioma, "select_material")
            )

            return

        valores = (
            self.tabla_materiales
            .item(
                seleccion[0],
                "values"
            )
        )

        self.material_number.delete(
            0,
            tk.END
        )

        self.material_number.insert(
            0,
            valores[0]
        )

        self.material_description.delete(
            0,
            tk.END
        )

        self.material_description.insert(
            0,
            valores[1]
        )


    def desactivar_material_seleccionado(self):

        seleccion = (
            self.tabla_materiales
            .selection()
        )

        if not seleccion:

            messagebox.showwarning(
                tr(self.idioma, "select_material_title"),
                tr(self.idioma, "select_material")
            )

            return

        valores = (
            self.tabla_materiales
            .item(
                seleccion[0],
                "values"
            )
        )

        material = valores[0]

        confirmar = messagebox.askyesno(
            tr(self.idioma, "deactivate_material_title"),
            tr(
                self.idioma,
                "deactivate_material_confirm",
                material=material
            )
        )

        if not confirmar:
            return

        desactivar_material(
            material
        )

        self.cargar_materiales()


    def limpiar_busqueda_material(self):

        self.material_search.delete(
            0,
            tk.END
        )

        self.cargar_materiales()



        # ==================================================
    # IMPORT XLSX
    # ==================================================

    def importar_xlsx(self):

        ruta = filedialog.askopenfilename(
            title=tr(self.idioma, "select_material_database"),
            filetypes=[
                ("Excel files", "*.xlsx")
            ]
        )

        if not ruta:
            return

        respuesta = messagebox.askyesnocancel(
            tr(self.idioma, "import_mode_title"),
            tr(self.idioma, "import_mode_message")
        )

        if respuesta is None:
            return

        if respuesta:

            modo = "ADD_UPDATE"
            nombre_modo = tr(
                self.idioma,
                "add_update_mode"
            )

        else:

            modo = "REPLACE"
            nombre_modo = tr(
                self.idioma,
                "replace_database_mode"
            )

            confirmar = messagebox.askyesno(
                tr(self.idioma, "confirm_replace_title"),
                tr(self.idioma, "confirm_replace_message")
            )

            if not confirmar:
                return

        try:

            resultado = importar_materiales(
                ruta,
                modo
            )

        except Exception as error:

            messagebox.showerror(
                tr(self.idioma, "import_error_title"),
                tr(
                    self.idioma,
                    "import_error",
                    error=error
                )
            )

            return

        self.cargar_materiales()

        messagebox.showinfo(
            tr(self.idioma, "import_completed_title"),
            tr(
                self.idioma,
                "import_completed",
                mode=nombre_modo,
                total=resultado["total_excel"],
                added=resultado["added"],
                updated=resultado["updated"],
                reactivated=resultado["reactivated"],
                deactivated=resultado["deactivated"]
            )
        )       