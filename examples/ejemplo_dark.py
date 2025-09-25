import tkinter as tk
from tkinter import ttk
import sv_ttk

root = tk.Tk()
root.title("Modo oscuro con ttk")

label = ttk.Label(root, text="Hola en modo oscuro")
label.pack(padx=20, pady=20)

button = ttk.Button(root, text="Un botón")
button.pack(pady=10)

# Activar tema oscuro
sv_ttk.set_theme("dark")

root.mainloop()
