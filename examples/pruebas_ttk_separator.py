import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Separadores en Grid")

# Configuramos la grilla para que las celdas se expandan
root.columnconfigure((0, 2), weight=1)
root.rowconfigure((0, 2), weight=1)

# --- Widgets en la grilla ---
ttk.Label(root, text="Celda (0, 0)").grid(row=0, column=0, padx=10, pady=10)
ttk.Label(root, text="Celda (0, 2)").grid(row=0, column=2, padx=10, pady=10)
ttk.Label(root, text="Celda (2, 0)").grid(row=2, column=0, padx=10, pady=10)
ttk.Label(root, text="Celda (2, 2)").grid(row=2, column=2, padx=10, pady=10)

# --- Separadores ---

# Separador VERTICAL en la columna 1
# Se estira de Norte a Sur (ns) y abarca 3 filas (rowspan=3)
sep_vertical = ttk.Separator(root, orient='vertical')
sep_vertical.grid(row=0, column=1, rowspan=3, sticky='ns')

# Separador HORIZONTAL en la fila 1
# Se estira de Este a Oeste (ew) y abarca 3 columnas (columnspan=3)
sep_horizontal = ttk.Separator(root, orient='horizontal')
sep_horizontal.grid(row=1, column=0, columnspan=3, sticky='ew')

root.mainloop()