import tkinter as tk
from tkinter import ttk, messagebox

from auth import iniciar_sesion
from admin_panel import AdminPanel
from pid_generator import PIDGenerator
from translations import LANGUAGES, tr
from packing_list_generator import PackingListGenerator


# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------

TIEMPO_INACTIVIDAD_MS = 30 * 60 * 1000


# -----------------------------------
# APLICACIÓN PRINCIPAL
# -----------------------------------

class PalletIDApp:

    def __init__(self):

        self.ventana = tk.Tk()

        self.ventana.title("Pallet ID System")
        self.ventana.geometry("700x560")
        self.ventana.resizable(False, False)

        self.usuario_actual = None
        self.idioma = "es"

        self.temporizador_inactividad = None

        # Detectar actividad del usuario
        self.ventana.bind_all(
            "<Any-KeyPress>",
            self.registrar_actividad
        )

        self.ventana.bind_all(
            "<Any-Button>",
            self.registrar_actividad
        )

        self.mostrar_login()

        self.ventana.mainloop()


    # -----------------------------------
    # LIMPIAR VENTANA
    # -----------------------------------

    def limpiar_ventana(self):

        for widget in self.ventana.winfo_children():
            widget.destroy()


    # -----------------------------------
    # CONTROL DE INACTIVIDAD
    # -----------------------------------

    def registrar_actividad(self, event=None):

        if self.usuario_actual is None:
            return

        self.reiniciar_temporizador()


    def reiniciar_temporizador(self):

        if self.temporizador_inactividad is not None:

            self.ventana.after_cancel(
                self.temporizador_inactividad
            )

        self.temporizador_inactividad = (
            self.ventana.after(
                TIEMPO_INACTIVIDAD_MS,
                self.cerrar_sesion_inactividad
            )
        )


    def cerrar_sesion_inactividad(self):

        if self.usuario_actual is None:
            return

        messagebox.showwarning(
            tr(self.idioma, "inactive_logout_title"),
            tr(self.idioma, "inactive_logout_message")
        )

        self.cerrar_sesion()


    # -----------------------------------
    # LOGIN
    # -----------------------------------

    def mostrar_login(self):

        self.usuario_actual = None

        if self.temporizador_inactividad is not None:

            self.ventana.after_cancel(
                self.temporizador_inactividad
            )

            self.temporizador_inactividad = None

        self.limpiar_ventana()

        self.ventana.geometry("700x560")

        idioma_nombre = (
            "Español"
            if self.idioma == "es"
            else "English"
        )

        idioma_var = tk.StringVar(
            value=idioma_nombre
        )

        titulo_app = tk.Label(
            self.ventana,
            text=tr(self.idioma, "app_title"),
            font=("Arial", 26, "bold")
        )

        titulo_app.pack(pady=(35, 20))

        tk.Label(
            self.ventana,
            text=tr(self.idioma, "language"),
            font=("Arial", 11, "bold")
        ).pack()

        selector_idioma = ttk.Combobox(
            self.ventana,
            values=list(LANGUAGES.keys()),
            textvariable=idioma_var,
            state="readonly",
            width=20,
            justify="center"
        )

        selector_idioma.pack(pady=(5, 20))

        etiqueta_usuario = tk.Label(
            self.ventana,
            text=tr(self.idioma, "employee_id"),
            font=("Arial", 12)
        )

        etiqueta_usuario.pack()

        entrada_usuario = tk.Entry(
            self.ventana,
            font=("Arial", 14),
            justify="center",
            width=25
        )

        entrada_usuario.pack(pady=10)

        etiqueta_password = tk.Label(
            self.ventana,
            text=tr(self.idioma, "password"),
            font=("Arial", 12)
        )

        etiqueta_password.pack()

        entrada_password = tk.Entry(
            self.ventana,
            font=("Arial", 14),
            justify="center",
            width=25,
            show="*"
        )

        entrada_password.pack(pady=10)


        def actualizar_idioma_login(event=None):

            self.idioma = LANGUAGES.get(
                idioma_var.get(),
                "es"
            )

            titulo_app.config(
                text=tr(
                    self.idioma,
                    "app_title"
                )
            )

            etiqueta_usuario.config(
                text=tr(
                    self.idioma,
                    "employee_id"
                )
            )

            etiqueta_password.config(
                text=tr(
                    self.idioma,
                    "password"
                )
            )

            boton_login.config(
                text=tr(
                    self.idioma,
                    "login_button"
                )
            )


        def login():

            self.idioma = LANGUAGES.get(
                idioma_var.get(),
                "es"
            )

            employee_id = (
                entrada_usuario
                .get()
                .strip()
            )

            password = (
                entrada_password
                .get()
            )

            if not employee_id or not password:

                messagebox.showwarning(
                    tr(
                        self.idioma,
                        "required_login_title"
                    ),
                    tr(
                        self.idioma,
                        "required_login_message"
                    )
                )

                return

            usuario = iniciar_sesion(
                employee_id,
                password
            )

            if usuario is None:

                messagebox.showerror(
                    tr(
                        self.idioma,
                        "login_error_title"
                    ),
                    tr(
                        self.idioma,
                        "login_error_message"
                    )
                )

                entrada_password.delete(
                    0,
                    tk.END
                )

                entrada_password.focus_set()

                return

            self.usuario_actual = usuario

            self.reiniciar_temporizador()

            self.mostrar_menu()


        boton_login = tk.Button(
            self.ventana,
            text=tr(
                self.idioma,
                "login_button"
            ),
            font=("Arial", 13, "bold"),
            width=20,
            height=2,
            command=login
        )

        boton_login.pack(pady=30)

        selector_idioma.bind(
            "<<ComboboxSelected>>",
            actualizar_idioma_login
        )

        entrada_usuario.bind(
            "<Return>",
            lambda event:
                entrada_password.focus_set()
        )

        entrada_password.bind(
            "<Return>",
            lambda event: login()
        )

        entrada_usuario.focus_set()


    # -----------------------------------
    # MENÚ PRINCIPAL
    # -----------------------------------

    def mostrar_menu(self):

        self.limpiar_ventana()

        usuario = self.usuario_actual

        self.ventana.geometry("750x550")

        tk.Label(
            self.ventana,
            text=tr(
                self.idioma,
                "app_title"
            ),
            font=("Arial", 24, "bold")
        ).pack(pady=25)

        tk.Label(
            self.ventana,
            text=(
                f"{tr(self.idioma, 'welcome')}, "
                f"{usuario['name']}"
            ),
            font=("Arial", 15)
        ).pack(pady=5)

        tk.Label(
            self.ventana,
            text=(
                f"{tr(self.idioma, 'employee_id')}: "
                f"{usuario['employee_id']}\n"
                f"{tr(self.idioma, 'role')}: "
                f"{usuario['role']}"
            ),
            font=("Arial", 11)
        ).pack(pady=10)

        # PID GENERATOR
        tk.Button(
            self.ventana,
            text=tr(
                self.idioma,
                "pid_generator"
            ),
            font=("Arial", 13, "bold"),
            width=30,
            height=2,
            command=lambda: PIDGenerator(
                self.ventana,
                self.usuario_actual,
                self.mostrar_menu,
                self.idioma
            )
        ).pack(pady=10)

        # PACKING LIST GENERATOR
        tk.Button(
            self.ventana,
            text=tr(
                self.idioma,
                "packing_list_generator"
            ),
            font=("Arial", 13, "bold"),
            width=30,
            height=2,
            command=self.abrir_packing_list_generator

        ).pack(pady=10)

        # ADMINISTRATION
        if usuario["role"] == "ADMIN":

            tk.Button(
                self.ventana,
                text=tr(
                    self.idioma,
                    "administration"
                ),
                font=("Arial", 13, "bold"),
                width=30,
                height=2,
                command=lambda: AdminPanel(
                    self.ventana,
                    self.usuario_actual,
                    self.mostrar_menu,
                    self.idioma
                )
            ).pack(pady=10)

        tk.Button(
            self.ventana,
            text=tr(
                self.idioma,
                "logout"
            ),
            font=("Arial", 12),
            width=20,
            command=self.cerrar_sesion
        ).pack(pady=25)


    # -----------------------------------
    # CERRAR SESIÓN
    # -----------------------------------

    def cerrar_sesion(self):

        self.usuario_actual = None

        if self.temporizador_inactividad is not None:

            self.ventana.after_cancel(
                self.temporizador_inactividad
            )

            self.temporizador_inactividad = None

        self.mostrar_login()
    def abrir_packing_list_generator(self):

        PackingListGenerator(
            self.ventana,
            self.usuario_actual,
            self.mostrar_menu,
            self.idioma
        )
# -----------------------------------
# INICIAR PROGRAMA
# -----------------------------------

if __name__ == "__main__":

    PalletIDApp()
