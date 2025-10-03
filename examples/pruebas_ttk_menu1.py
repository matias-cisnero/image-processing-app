import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk  # pip install ttkthemes

# ====== Ventana principal con ttkthemes ======
root = ThemedTk(theme="arc")  # probá también: "equilux", "plastik", "breeze"
root.title("Demo Menubuttons con ttkthemes")
root.geometry("700x400")

# ====== Frame para la barra de menús ======
menubar_frame = ttk.Frame(root)
menubar_frame.pack(fill="x", side="top")

# Función auxiliar para crear menubuttons con menú
def crear_menubutton(parent, texto, opciones):
    menubtn = ttk.Menubutton(parent, text=texto)
    menu = tk.Menu(menubtn, tearoff=0, bg="#fcfdfd", fg="#7B7E83",
               activebackground="#cfd6e6", activeforeground="white",
               font=("Segoe UI", 10))

    for op in opciones:
        if op == "sep":
            menu.add_separator()
        elif isinstance(op, tuple):
            label, cmd = op
            menu.add_command(label=label, command=cmd)
        else:
            menu.add_command(label=op, command=lambda o=op: print(f"Elegiste {o}"))

    menubtn["menu"] = menu
    return menubtn

# ====== Menús ======
archivo_menu = crear_menubutton(
    menubar_frame, "Archivo",
    [("Nuevo", lambda: print("Nuevo archivo")),
     ("Abrir", lambda: print("Abrir archivo")),
     "sep",
     ("Salir", root.quit)]
)

editar_menu = crear_menubutton(
    menubar_frame, "Editar",
    [("Copiar", lambda: print("Copiar")),
     ("Pegar", lambda: print("Pegar")),
     ("Cortar", lambda: print("Cortar"))]
)

ver_menu = crear_menubutton(
    menubar_frame, "Ver",
    [("Zoom +", lambda: print("Zoom In")),
     ("Zoom -", lambda: print("Zoom Out")),
     "sep",
     ("Pantalla completa", lambda: print("Pantalla completa"))]
)

ayuda_menu = crear_menubutton(
    menubar_frame, "Ayuda",
    [("Documentación", lambda: print("Abrir docs")),
     ("Acerca de", lambda: print("Acerca de"))]
)

# ====== Colocarlos a la derecha ======
for menu in [archivo_menu, editar_menu, ver_menu, ayuda_menu]:
    menu.pack(side="right", padx=5, pady=5)

# ====== Contenido de prueba ======
contenido = ttk.Label(root, text="Ventana principal con Menubuttons estilizados con ttkthemes",
                      font=("Segoe UI", 12), anchor="center", padding=20)
contenido.pack(expand=True, fill="both")

root.mainloop()
