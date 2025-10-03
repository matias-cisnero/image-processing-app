import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú estilo ttk")
        self._crear_menu()

    def _crear_menu(self):
        # Frame superior que simula la barra de menús
        barra_menu = ttk.Frame(self.root)
        barra_menu.pack(fill="x")

        # ===== Menú Archivo =====
        archivo_btn = ttk.Menubutton(barra_menu, text="Archivo")
        archivo_btn.pack(side="left", padx=5)

        archivo_menu = tk.Menu(archivo_btn, tearoff=0,
                               bg="#2e2e2e", fg="white",
                               activebackground="#444", activeforeground="white",
                               font=("Segoe UI", 10))

        archivo_menu.add_command(label="Cargar Imagen...", command=self._cargar_imagen, accelerator="Ctrl+O")
        archivo_menu.add_command(label="Guardar Imagen Como...", command=self._guardar_imagen_como, accelerator="Ctrl+S")
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)

        archivo_btn["menu"] = archivo_menu

        # ===== Otro menú =====
        ayuda_btn = ttk.Menubutton(barra_menu, text="Ayuda")
        ayuda_btn.pack(side="left", padx=5)

        ayuda_menu = tk.Menu(ayuda_btn, tearoff=0,
                             bg="#2e2e2e", fg="white",
                             activebackground="#444", activeforeground="white",
                             font=("Segoe UI", 10))
        ayuda_menu.add_command(label="Acerca de...", command=lambda: print("Mostrando Acerca de..."))
        ayuda_btn["menu"] = ayuda_menu

    def _cargar_imagen(self):
        print("Cargar imagen...")

    def _guardar_imagen_como(self):
        print("Guardar imagen como...")

# Demo
if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = App(root)
    root.mainloop()
