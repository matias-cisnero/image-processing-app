import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Checkbutton]========

estado = tk.StringVar() # hay más tipos de tk.variables
def mostrar_estado(): print(estado.get()) #.get() para obtener el string de eso
tk.Checkbutton(text="Verificar", variable=estado, onvalue="SI", offvalue="NO", command=mostrar_estado).pack()

#=======[Radiobutton]========

opcion = tk.StringVar()
def mostrar_opcion(): print(opcion.get())
tk.Radiobutton(text="Selecciona una opción", variable=opcion, value="jeje1", command=mostrar_opcion).pack()
tk.Radiobutton(text="Selecciona una opción", variable=opcion, value="JUAJUA2", command=mostrar_opcion).pack()
tk.Radiobutton(text="Selecciona una opción", variable=opcion, value="UHHHHHHH3", command=mostrar_opcion).pack()

#=======[Scale]========

numero = tk.IntVar()
tk.Scale(from_=0, to=100, orient="horizontal", variable=numero ,resolution=5, showvalue=True).pack() # También puede tener command
tk.Label(textvariable=numero).pack() # Mostrarlo en un label

tk.Scale(from_=0, to=100, orient="vertical", variable=numero ,resolution=5, showvalue=True).pack() # También puede tener command

# Iniciar el bucle de eventos
ventana.mainloop()