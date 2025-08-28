import tkinter as tk

# Ventana principal
ventana = tk.Tk()
ventana.title("Mis Primeros Labels")
ventana.geometry("600x600+300+100") # Ancho x Alto + posición desde izq + posición desde arriba
ventana.iconbitmap("favicon.ico")
ventana.config(bg="#dbeefc")

#=======[Entry]========

# ======================================================================
# Utilidad: [textvariable, show, exportselection]
# ======================================================================

variable = tk.StringVar()
tk.Entry(textvariable=variable).pack() # Cambiar el texto de la variable
tk.Label(textvariable=variable).pack() # Mostrarlo en un label

tk.Entry(show="*").pack() # Cambia el contenido por el caracter específicado

tk.Entry(exportselection=False) # Para copiar ese texto en el portapapeles o no.

# ======================================================================
# Interacción: [.get(), .insert(indice, texto), delete(desde, hasta)]
# ======================================================================

escritura = tk.Entry()
escritura.pack()
def printear():
    texto = escritura.get() # <-------- importante
    print(texto)
tk.Button(text="Printear texto de arriba", command=printear).pack()

def convertir_a_email():
    escritura.insert(tk.END, "@gmail.com") # <-------- importante
tk.Button(text="Convertir a email", command=convertir_a_email).pack()

def borrar_texto():
    escritura.delete(2, tk.END) # <-------- importante
tk.Button(text="Dejar solo 2 caracteres", command=borrar_texto).pack()

# Iniciar el bucle de eventos
ventana.mainloop()