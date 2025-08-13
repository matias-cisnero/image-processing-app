import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Frame]========

# ===========================================
# Geometría: [.pack(), .grid(), .place()]
# ===========================================
# ¡NUNCA MEZCLAR GRID Y PACK EN UN MISMO FRAME O VENTANA!

# .pack() es para apilar cosas una debajo de la otra
# .grid() ¡EL MÁS RECOMENDADO! divide en grillas

frame1 = tk.Frame(bg="lightblue", padx=3, pady=3) # pad = relleno
frame1.grid(row=0, column=0, padx=5, pady=5) # <------- margen externo
# rawspan, columnspan permite que los widgets ocupen varias filas o columnas, widget.grid(row=0, column=0, columnspan=2)

frame2 = tk.Frame(bg="lightblue", padx=3, pady=3) # pad = relleno
frame2.grid(row=0, column=1, ipadx=5, ipady=5) # <------- margen interno


# Labels necesarios

tk.Label(frame1, text="Unahur").pack()

tk.Label(frame1, text="Unahur", font=("Arial", 14, "bold")).pack()

tk.Label(frame1, text="Unahur", fg="white", bg="#2C3E50").pack() # fg + bg (color de letra y fondo)

tk.Label(frame2, text="Unahur", width=20, height=1).pack() # width + height

tk.Label(frame2, text="Unahur", bd=10).pack() # grosor del borde de la etiqueta

tk.Label(frame2, text="Unahur", relief="solid").pack() # Opciones: [flat, raised, sunken, solid, ridge, groove]

tk.Label(frame2, text="Unahur", cursor="hand2").pack() # cambia la apariencia del cursor al pasar por encima

# Iniciar el bucle de eventos
ventana.mainloop()