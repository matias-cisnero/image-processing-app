import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Label]========

# ======================================================================
# Contenido: [text, textvariable, image, compound]
# ======================================================================

tk.Label(text="Hola, Tkinter!").pack() # Se puede colocar tk.Label(ventana) para decir que se ponga en esa ventana

texto_dinamico = tk.StringVar()
texto_dinamico.set("Valor inicial")
tk.Label(textvariable=texto_dinamico).pack()

mi_imagen = tk.PhotoImage(file="barco.png")
tk.Label(image=mi_imagen).pack()

tk.Label(text="Logo", image=mi_imagen, compound="bottom").pack() # Indica donde se pone la imagen respecto al texto

# ======================================================================
# Estilo y Apariencia: [font, fg, bg, width, height, bd, relief, cursor]
# ======================================================================

tk.Label(text="Unahur").pack()

tk.Label(text="Unahur", font=("Arial", 14, "bold")).pack()

tk.Label(text="Unahur", fg="white", bg="#2C3E50").pack() # fg + bg (color de letra y fondo)

tk.Label(text="Unahur", width=20, height=1).pack() # width + height

tk.Label(text="Unahur", bd=10).pack() # grosor del borde de la etiqueta

tk.Label(text="Unahur", relief="solid").pack() # Opciones: [flat, raised, sunken, solid, ridge, groove]

tk.Label(text="Unahur", cursor="hand2").pack() # cambia la apariencia del cursor al pasar por encima

# ======================================================================
# Posicionamiento: [anchor, justify, padx, pady, wraplength]
# ======================================================================

tk.Label(text="Posicionamiento", width=20, anchor="w").pack() # Opciones: [n, s, e, w, ne, nw, se, sw, center]

tk.Label(text="Texto\nmultilínea", justify="right").pack() #\n para salto de linea

tk.Label(text="Relleno", relief="solid", bd=1, padx=10, pady=5).pack()

tk.Label(text="Este texto muy largo se cortará...", wraplength=150).pack()

# Iniciar el bucle de eventos
ventana.mainloop()