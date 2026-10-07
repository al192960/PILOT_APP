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
from ui_branding import mostrar_logo


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

        mostrar_logo(
            self.ventana,
            ancho=150,
            pady=(6, 3)
        )

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "admin_title"),
            font=("Arial", 22, "bold")
        ).pack(pady=6)

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
            pady=8
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
        ).pack(pady=5)


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
            height=9
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

        frame_acciones = tk.Frame(
            parent
        )

        frame_acciones.pack(
            pady=6
        )

        tk.Button(
            frame_acciones,
            text=tr(self.idioma, "edit_selected_user"),
            width=20,
            command=self.editar_usuario_seleccionado
        ).grid(
            row=0,
            column=0,
            padx=6
        )

        tk.Button(
            frame_acciones,
            text=tr(self.idioma, "reset_password"),
            width=22,
            command=self.restablecer_password_seleccionado
        ).grid(
            row=0,
            column=1,
            padx=6
        )

        tk.Button(
            frame_acciones,
            text=tr(self.idioma, "toggle_user_status"),
            width=24,
            command=self.cambiar_estado_usuario_seleccionado
        ).grid(
            row=0,
            column=2,
            padx=6
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
    # ADMINISTRACIÓN DE USUARIOS
    # ==================================================

    def obtener_employee_id_seleccionado(self):

        seleccion = self.tabla_users.selection()

        if not seleccion:

            messagebox.showwarning(
                tr(self.idioma, "select_user_title"),
                tr(self.idioma, "select_user")
            )

            return None

        valores = self.tabla_users.item(
            seleccion[0],
            "values"
        )

        if not valores:
            return None

        return str(valores[0])


    def contar_admins_activos(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE role = 'ADMIN'
              AND active = 1
        """)

        total = cursor.fetchone()[0]

        conexion.close()

        return total


    def editar_usuario_seleccionado(self):

        employee_id = (
            self.obtener_employee_id_seleccionado()
        )

        if employee_id is None:
            return

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                employee_id,
                name,
                role,
                can_create_packing_list,
                active
            FROM users
            WHERE employee_id = ?
        """, (
            employee_id,
        ))

        usuario = cursor.fetchone()

        conexion.close()

        if usuario is None:

            messagebox.showerror(
                tr(self.idioma, "user_not_found_title"),
                tr(self.idioma, "user_not_found")
            )

            self.cargar_usuarios()
            return

        ventana_editar = tk.Toplevel(
            self.ventana
        )

        ventana_editar.title(
            tr(self.idioma, "edit_user_title")
        )

        ventana_editar.geometry("430x330")
        ventana_editar.resizable(False, False)
        ventana_editar.transient(self.ventana)
        ventana_editar.grab_set()

        tk.Label(
            ventana_editar,
            text=tr(self.idioma, "edit_user_title"),
            font=("Arial", 16, "bold")
        ).pack(
            pady=(18, 12)
        )

        frame = tk.Frame(
            ventana_editar
        )

        frame.pack(
            padx=25,
            fill="x"
        )

        tk.Label(
            frame,
            text=f"{tr(self.idioma, 'employee_id')}:"
        ).grid(
            row=0,
            column=0,
            sticky="e",
            padx=8,
            pady=8
        )

        tk.Label(
            frame,
            text=usuario[1],
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=8,
            pady=8
        )

        tk.Label(
            frame,
            text=f"{tr(self.idioma, 'name')}:"
        ).grid(
            row=1,
            column=0,
            sticky="e",
            padx=8,
            pady=8
        )

        entrada_nombre = tk.Entry(
            frame,
            width=28
        )

        entrada_nombre.grid(
            row=1,
            column=1,
            padx=8,
            pady=8
        )

        entrada_nombre.insert(
            0,
            usuario[2]
        )

        tk.Label(
            frame,
            text=f"{tr(self.idioma, 'role')}:"
        ).grid(
            row=2,
            column=0,
            sticky="e",
            padx=8,
            pady=8
        )

        combo_role = ttk.Combobox(
            frame,
            values=[
                "USER",
                "GROUP_LEADER",
                "ADMIN"
            ],
            state="readonly",
            width=25
        )

        combo_role.grid(
            row=2,
            column=1,
            padx=8,
            pady=8
        )

        combo_role.set(
            usuario[3]
        )

        packing_var = tk.IntVar(
            value=usuario[4]
        )

        check_packing = tk.Checkbutton(
            frame,
            text=tr(
                self.idioma,
                "allow_packing_list"
            ),
            variable=packing_var
        )

        check_packing.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=12
        )

        def actualizar_permiso_role(event=None):

            if combo_role.get() in (
                "ADMIN",
                "GROUP_LEADER"
            ):

                packing_var.set(1)
                check_packing.config(
                    state="disabled"
                )

            else:

                check_packing.config(
                    state="normal"
                )

        combo_role.bind(
            "<<ComboboxSelected>>",
            actualizar_permiso_role
        )

        actualizar_permiso_role()

        def guardar_cambios():

            nombre = (
                entrada_nombre
                .get()
                .strip()
            )

            nuevo_role = combo_role.get()
            packing = packing_var.get()

            if not nombre:

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "required_fields_title"
                    ),
                    tr(
                        self.idioma,
                        "user_name_required"
                    ),
                    parent=ventana_editar
                )

                return

            if nuevo_role in (
                "ADMIN",
                "GROUP_LEADER"
            ):
                packing = 1

            es_usuario_actual = (
                employee_id
                == self.usuario_actual["employee_id"]
            )

            if (
                es_usuario_actual
                and nuevo_role != "ADMIN"
            ):

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "cannot_change_own_admin_role_title"
                    ),
                    tr(
                        self.idioma,
                        "cannot_change_own_admin_role"
                    ),
                    parent=ventana_editar
                )

                return

            if (
                usuario[3] == "ADMIN"
                and nuevo_role != "ADMIN"
                and usuario[5] == 1
                and self.contar_admins_activos() <= 1
            ):

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "last_admin_title"
                    ),
                    tr(
                        self.idioma,
                        "last_admin_role_message"
                    ),
                    parent=ventana_editar
                )

                return

            conexion = conectar()

            try:

                cursor = conexion.cursor()

                cursor.execute("""
                    UPDATE users
                    SET
                        name = ?,
                        role = ?,
                        can_create_packing_list = ?
                    WHERE employee_id = ?
                """, (
                    nombre,
                    nuevo_role,
                    packing,
                    employee_id
                ))

                conexion.commit()

            except Exception as error:

                conexion.rollback()

                messagebox.showerror(
                    tr(
                        self.idioma,
                        "user_update_error_title"
                    ),
                    tr(
                        self.idioma,
                        "user_update_error",
                        error=error
                    ),
                    parent=ventana_editar
                )

                return

            finally:

                conexion.close()

            messagebox.showinfo(
                tr(
                    self.idioma,
                    "user_updated_title"
                ),
                tr(
                    self.idioma,
                    "user_updated",
                    employee_id=employee_id
                ),
                parent=ventana_editar
            )

            ventana_editar.destroy()
            self.cargar_usuarios()

        frame_botones = tk.Frame(
            ventana_editar
        )

        frame_botones.pack(
            pady=15
        )

        tk.Button(
            frame_botones,
            text=tr(self.idioma, "save_changes"),
            width=16,
            command=guardar_cambios
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        tk.Button(
            frame_botones,
            text=tr(self.idioma, "cancel"),
            width=12,
            command=ventana_editar.destroy
        ).grid(
            row=0,
            column=1,
            padx=8
        )

        entrada_nombre.focus_set()


    def restablecer_password_seleccionado(self):

        employee_id = (
            self.obtener_employee_id_seleccionado()
        )

        if employee_id is None:
            return

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT name
            FROM users
            WHERE employee_id = ?
        """, (
            employee_id,
        ))

        resultado = cursor.fetchone()

        conexion.close()

        if resultado is None:

            messagebox.showerror(
                tr(self.idioma, "user_not_found_title"),
                tr(self.idioma, "user_not_found")
            )

            self.cargar_usuarios()
            return

        ventana_password = tk.Toplevel(
            self.ventana
        )

        ventana_password.title(
            tr(self.idioma, "reset_password")
        )

        ventana_password.geometry("420x300")
        ventana_password.resizable(False, False)
        ventana_password.transient(self.ventana)
        ventana_password.grab_set()

        tk.Label(
            ventana_password,
            text=tr(self.idioma, "reset_password"),
            font=("Arial", 16, "bold")
        ).pack(
            pady=(20, 8)
        )

        tk.Label(
            ventana_password,
            text=(
                f"{resultado[0]} "
                f"({employee_id})"
            )
        ).pack(
            pady=(0, 12)
        )

        frame = tk.Frame(
            ventana_password
        )

        frame.pack()

        tk.Label(
            frame,
            text=f"{tr(self.idioma, 'new_password')}:"
        ).grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="e"
        )

        nueva_password = tk.Entry(
            frame,
            show="*",
            width=24
        )

        nueva_password.grid(
            row=0,
            column=1,
            padx=8,
            pady=8
        )

        tk.Label(
            frame,
            text=f"{tr(self.idioma, 'confirm_password')}:"
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=8,
            sticky="e"
        )

        confirmar_password = tk.Entry(
            frame,
            show="*",
            width=24
        )

        confirmar_password.grid(
            row=1,
            column=1,
            padx=8,
            pady=8
        )

        def guardar_password():

            password_1 = nueva_password.get()
            password_2 = confirmar_password.get()

            if not password_1 or not password_2:

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "password_required_title"
                    ),
                    tr(
                        self.idioma,
                        "password_required"
                    ),
                    parent=ventana_password
                )

                return

            if password_1 != password_2:

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "password_mismatch_title"
                    ),
                    tr(
                        self.idioma,
                        "password_mismatch"
                    ),
                    parent=ventana_password
                )

                return

            password_hash = generar_hash(
                password_1
            )

            conexion = conectar()

            try:

                cursor = conexion.cursor()

                cursor.execute("""
                    UPDATE users
                    SET password_hash = ?
                    WHERE employee_id = ?
                """, (
                    password_hash,
                    employee_id
                ))

                conexion.commit()

            except Exception as error:

                conexion.rollback()

                messagebox.showerror(
                    tr(
                        self.idioma,
                        "password_reset_error_title"
                    ),
                    tr(
                        self.idioma,
                        "password_reset_error",
                        error=error
                    ),
                    parent=ventana_password
                )

                return

            finally:

                conexion.close()

            messagebox.showinfo(
                tr(
                    self.idioma,
                    "password_reset_title"
                ),
                tr(
                    self.idioma,
                    "password_reset_success",
                    employee_id=employee_id
                ),
                parent=ventana_password
            )

            ventana_password.destroy()

        frame_botones = tk.Frame(
            ventana_password
        )

        frame_botones.pack(
            pady=18
        )

        tk.Button(
            frame_botones,
            text=tr(self.idioma, "save_changes"),
            width=16,
            command=guardar_password
        ).grid(
            row=0,
            column=0,
            padx=8
        )

        tk.Button(
            frame_botones,
            text=tr(self.idioma, "cancel"),
            width=12,
            command=ventana_password.destroy
        ).grid(
            row=0,
            column=1,
            padx=8
        )

        nueva_password.focus_set()


    def cambiar_estado_usuario_seleccionado(self):

        employee_id = (
            self.obtener_employee_id_seleccionado()
        )

        if employee_id is None:
            return

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                name,
                role,
                active
            FROM users
            WHERE employee_id = ?
        """, (
            employee_id,
        ))

        usuario = cursor.fetchone()

        conexion.close()

        if usuario is None:

            messagebox.showerror(
                tr(self.idioma, "user_not_found_title"),
                tr(self.idioma, "user_not_found")
            )

            self.cargar_usuarios()
            return

        nombre = usuario[0]
        role = usuario[1]
        activo = usuario[2] == 1

        if activo:

            if (
                employee_id
                == self.usuario_actual["employee_id"]
            ):

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "cannot_deactivate_self_title"
                    ),
                    tr(
                        self.idioma,
                        "cannot_deactivate_self"
                    )
                )

                return

            if (
                role == "ADMIN"
                and self.contar_admins_activos() <= 1
            ):

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "last_admin_title"
                    ),
                    tr(
                        self.idioma,
                        "last_admin_deactivate_message"
                    )
                )

                return

            confirmar = messagebox.askyesno(
                tr(
                    self.idioma,
                    "deactivate_user_title"
                ),
                tr(
                    self.idioma,
                    "deactivate_user_confirm",
                    name=nombre,
                    employee_id=employee_id
                )
            )

            if not confirmar:
                return

            nuevo_estado = 0
            mensaje_titulo = (
                "user_deactivated_title"
            )
            mensaje = "user_deactivated"

        else:

            confirmar = messagebox.askyesno(
                tr(
                    self.idioma,
                    "activate_user_title"
                ),
                tr(
                    self.idioma,
                    "activate_user_confirm",
                    name=nombre,
                    employee_id=employee_id
                )
            )

            if not confirmar:
                return

            nuevo_estado = 1
            mensaje_titulo = (
                "user_activated_title"
            )
            mensaje = "user_activated"

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE users
                SET active = ?
                WHERE employee_id = ?
            """, (
                nuevo_estado,
                employee_id
            ))

            conexion.commit()

        except Exception as error:

            conexion.rollback()

            messagebox.showerror(
                tr(
                    self.idioma,
                    "user_status_error_title"
                ),
                tr(
                    self.idioma,
                    "user_status_error",
                    error=error
                )
            )

            return

        finally:

            conexion.close()

        messagebox.showinfo(
            tr(
                self.idioma,
                mensaje_titulo
            ),
            tr(
                self.idioma,
                mensaje,
                employee_id=employee_id
            )
        )

        self.cargar_usuarios()


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