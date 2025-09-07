import tkinter as tk
from tkinter import ttk

# --- Funciones de ejemplo ---
def funcion_guardar():
    print("Guardando archivo...")

def funcion_abrir():
    print("Abriendo archivo...")


# --- Configuración de la Ventana ---
root = tk.Tk()
root.title("Botones con Íconos")
root.geometry("300x500")

# --- Carga de Imágenes ---
# Se recomienda cargar todas las imágenes una sola vez
try:
    icono_guardar = tk.PhotoImage(file="icons/carga-de-carpeta.png").subsample(5,5) 
    icono_abrir = tk.PhotoImage(file="icons/disco.png").subsample(5,5) 
except tk.TclError:
    print("Error: Asegúrate de tener los archivos 'guardar_icono.png' y 'abrir_icono.png' en la carpeta.")
    # Creamos imágenes dummy si no se encuentran, para que el programa no falle
    icono_guardar = tk.PhotoImage()
    icono_abrir = tk.PhotoImage()


# --- Creación de Widgets ---

# 1. Label que solo muestra una imagen
label_info = ttk.Label(root, image=icono_abrir, text="Abrir Archivo", compound='top')
label_info.pack(pady=10)
label_info.image = icono_abrir # Anclamos la referencia


# 2. Botón con ícono a la izquierda del texto 💾
boton1 = ttk.Button(
    root,
    text="Guardar",
    image=icono_guardar,
    compound="left",
    command=funcion_guardar
)
boton1.pack(pady=5, padx=20, fill='x')
boton1.image = icono_guardar # ✅ ¡El truco para que no desaparezca!


# 3. Botón con ícono arriba del texto
boton2 = ttk.Button(
    root,
    text="Abrir",
    image=icono_abrir,
    compound="top",
    command=funcion_abrir
)
boton2.pack(pady=5, padx=20, fill='x')
boton2.image = icono_abrir # ✅ Anclamos la referencia también aquí

root.mainloop()