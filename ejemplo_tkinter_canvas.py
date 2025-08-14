import tkinter as tk

ventana = tk.Tk()
ventana.title("Demostración de Canvas")

# Crear el lienzo
lienzo = tk.Canvas(ventana, width=600, height=400, bg="white")
lienzo.pack(pady=10)

# --- Dibujar objetos y guardar sus IDs ---

# 1. Un rectángulo azul como fondo del cielo
lienzo.create_rectangle(0, 0, 600, 250, fill="#87CEEB", outline="")

# 2. Un óvalo verde como suelo
lienzo.create_oval(-100, 200, 700, 500, fill="#228B22", outline="")

# 3. Una línea para el tronco de un árbol
lienzo.create_line(100, 250, 100, 180, fill="#8B4513", width=10)

# 4. Un polígono para las hojas del árbol
id_arbol = lienzo.create_polygon(
    50, 200, 100, 120, 150, 200,
    fill="darkgreen", outline="black"
)

# 5. Un círculo amarillo para el sol (guardamos su ID para moverlo)
id_sol = lienzo.create_oval(500, 50, 560, 110, fill="yellow", outline="orange", width=3)

# 6. Texto en el lienzo
lienzo.create_text(
    300, 20, text="Mi Paisaje en Tkinter",
    font=("Arial", 20, "bold"), fill="black"
)

# 7. Un botón DENTRO del lienzo
def cambiar_color_arbol():
    """Cambia el color de las hojas del árbol usando su ID."""
    lienzo.itemconfig(id_arbol, fill="orange")
    print("¡El árbol es ahora otoñal!")

boton = tk.Button(ventana, text="Cambiar a Otoño", command=cambiar_color_arbol)
lienzo.create_window(10, 10, anchor="nw", window=boton)


# --- Hacer que el sol sea arrastrable ---
# Las funciones de evento reciben un parámetro 'event' con info como las coordenadas del ratón
def empezar_arrastre(event):
    # Guardamos el objeto sobre el que se hizo clic
    widget = event.widget
    widget.drag_id = widget.find_closest(event.x, event.y)[0]
    widget.drag_x = event.x
    widget.drag_y = event.y

def arrastrar(event):
    widget = event.widget
    # Calculamos cuánto se movió el ratón
    dx = event.x - widget.drag_x
    dy = event.y - widget.drag_y
    # Movemos el objeto esa misma cantidad
    if widget.drag_id == id_sol: # Solo movemos el sol
        widget.move(widget.drag_id, dx, dy)
    # Actualizamos la posición del ratón
    widget.drag_x = event.x
    widget.drag_y = event.y

# Vincular eventos del ratón a las funciones
lienzo.bind("<Button-1>", empezar_arrastre) # Clic izquierdo
lienzo.bind("<B1-Motion>", arrastrar) # Clic izquierdo y arrastrar

ventana.mainloop()