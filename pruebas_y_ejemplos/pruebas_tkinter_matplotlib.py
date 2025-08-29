import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Matplotlib en Tkinter")

# Creamos figura de matplotlib
fig = Figure(figsize=(4,3), dpi=100)
ax = fig.add_subplot(111)
ax.plot([0,1,2,3], [0,1,4,9], marker="o")

# Insertamos en Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

root.mainloop()
