import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x300")
root.title("Transparencia con Tk/ttk")

# 80% opaco
root.attributes("-alpha", 0.8)

label = ttk.Label(root, text="Hola Matías 😎", font=("Segoe UI", 16))
label.pack(pady=40)

button = ttk.Button(root, text="Un botón")
button.pack(pady=20)

root.mainloop()
