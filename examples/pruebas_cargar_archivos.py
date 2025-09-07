import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

# Ventana principal
ventana = tk.Tk()
ventana.title("Visor FileDialog y Pillow")
ventana.geometry("500x500") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[filedialog]========

# askopenfilename()	Abre el diálogo de "Abrir" para seleccionar un solo archivo. Devuelve la ruta completa al archivo, o una cadena vacía si el usuario cancela.
# asksaveasfilename()	Abre el diálogo de "Guardar como". Devuelve la ruta y el nombre que el usuario eligió para guardar, o una cadena vacía si cancela.
# askopenfilenames()	Igual que la primera, pero permite seleccionar múltiples archivos. Devuelve una tupla de rutas.
# askdirectory()	Abre un diálogo para seleccionar una carpeta (un directorio). Devuelve la ruta a la carpeta.

matriz = None

def seleccionar_y_cargar_imagen():
    ruta_imagen = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=(
            ("Archivos de imagen", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Todos los archivos", "*.*")
        )
    )

    if not ruta_imagen:
        print("No se seleccionó ninguna imagen.")
        return
    
    print(f"Ruta seleccionada: {ruta_imagen}")

    try:
        imagen_pil = Image.open(ruta_imagen)
        imagen_pil.thumbnail((400, 400)) # Opcional

        pixeles = np.array(imagen_pil)
        print(f"Tipo: {type(pixeles)}")

        imagen_tk = ImageTk.PhotoImage(imagen_pil)
        label_imagen.config(image=imagen_tk)

        label_imagen.image = imagen_tk
    
    except Exception as e:
        print(f"Error al cargar la imagen: {e}")
        label_imagen.config(text=f"Error al abrir:\n{ruta_imagen}", image='')

# Botón que llama a la función para abrir el diálogo
boton_seleccionar = tk.Button(
    ventana,
    text="Seleccionar Imagen...",
    command=seleccionar_y_cargar_imagen,
    font=("Arial", 12)
)
boton_seleccionar.pack(pady=10)

# Label donde se mostrará la imagen
label_imagen = tk.Label(ventana)
label_imagen.pack(padx=10, pady=10, expand=True)

ventana.mainloop()