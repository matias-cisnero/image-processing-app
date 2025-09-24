import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
root = ctk.CTk() # Ventana principal de CustomTkinter
root.geometry("300x250")

# 1. Widget de CustomTkinter
btn_ctk = ctk.CTkButton(root, text="Botón Moderno (CTk)")
btn_ctk.pack(pady=10)

# 2. Widget de ttk
progress_ttk = ttk.Progressbar(root, length=200, mode='indeterminate')
progress_ttk.pack(pady=10)
progress_ttk.start()

# 3. Widget de tkinter clásico
canvas_tk = tk.Canvas(root, width=200, height=50, bg="purple")
canvas_tk.pack(pady=10)
canvas_tk.create_text(100, 25, text="Canvas Clásico (tk)", fill="white")
root.mainloop()