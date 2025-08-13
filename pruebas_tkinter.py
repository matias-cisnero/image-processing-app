import tkinter as tk

#=======================
#       Ventana
#=======================

# Ventana principal
ventana = tk.Tk()
ventana.title("Mi Primera Ventana")
ventana.geometry("400x300+600+200") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.resizable(True, True)
ventana.minsize(400, 300)
ventana.maxsize(800, 600)
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")
ventana.attributes("-alpha", 0.4)
ventana.attributes("-topmost", True)
#ventana.withdraw() # Oculta la ventana
#ventana.deiconify() # Muestra la venatana si estaba oculta o minimizada
#ventana.destroy() # Cierra cierra la ventana terminando el mainloop

#=======================
#       Widgets
#=======================

"""
Lista de widgets = [Label, Button, Entry, Text, Frame, Canvas, Checkbutton, Radiobutton,
Scale, Scrollbar, Menubutton, Menu, Listbox, Toplevel]
"""

# Agregar una etiqueta o widget
etiqueta = tk.Label(ventana, text="Hola, Tkinter!") # Se coloca en que ventana se debe poner
etiqueta.pack(pady=20) # "pack" es un gestor de geometría simple

# Iniciar el bucle de eventos
ventana.mainloop()