import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Button]========

# Iniciar el bucle de eventos
ventana.mainloop()