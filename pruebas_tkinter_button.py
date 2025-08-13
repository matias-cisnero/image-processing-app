import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Button]========

# ===========================================================================================================
# Comportamiento: [command, state]
# ===========================================================================================================

def accion(): print("¡Botón presionado!")
tk.Button(command=accion).pack() # Esto solo lo imprime en consola

tk.Button(text="No tocar", state=tk.DISABLED).pack() # Deshabilita el botón (DISABLED, NORMAL)

# ===========================================================================================================
# Contenido: [text, textvariable, image, compound]
# ===========================================================================================================

"Igual que label"

# ===========================================================================================================
# Estilo y Apariencia: [font, fg, bg, width, height, bd, relief, cursor, activebackground, activeforeground]
# ===========================================================================================================

"Igual que label la mayoría"

tk.Button(text="cambio de color al presionarme", activebackground="lightblue").pack()

tk.Button(text="cambio de color al presionarme", activeforeground="lightblue").pack()

# Iniciar el bucle de eventos
ventana.mainloop()