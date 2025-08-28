import tkinter as tk

ventana = tk.Tk()
ventana.title("Demo de Listbox")
ventana.geometry("350x300")

def item_seleccionado(evento):
    # .curselection() devuelve los índices, no el texto
    indices_seleccionados = lista.curselection()
    if not indices_seleccionados: # Si la tupla está vacía
        return
    
    # Obtenemos el primer índice seleccionado
    primer_indice = indices_seleccionados[0]
    # Usamos el índice para obtener el texto con .get()
    item_texto = lista.get(primer_indice)
    print(f"Índice: {primer_indice}, Valor: {item_texto}")
    etiqueta_resultado.config(text=f"Seleccionado: {item_texto}")

marco = tk.Frame(ventana)
marco.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(marco)
scrollbar.pack(side="right", fill="y")

lista = tk.Listbox(marco, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
lista.pack(side="left", fill="both", expand=True)
scrollbar.config(command=lista.yview)

# Llenar la lista
paises = ["Argentina", "Brasil", "Chile", "Colombia", "Ecuador", "México", "Perú", "Uruguay", "Venezuela"]
for pais in paises:
    lista.insert(tk.END, pais)

# Vincular el evento de selección a nuestra función
lista.bind("<<ListboxSelect>>", item_seleccionado)

etiqueta_resultado = tk.Label(ventana, text="Ningún país seleccionado")
etiqueta_resultado.pack(pady=5)

ventana.mainloop()