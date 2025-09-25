import tkinter as tk

def draw_gradient(canvas, color1, color2):
    # tamaño del canvas
    width = canvas.winfo_reqwidth()
    height = canvas.winfo_reqheight()

    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r_ratio = (r2 - r1) / height
    g_ratio = (g2 - g1) / height
    b_ratio = (b2 - b1) / height

    for i in range(height):
        nr = int(r1 + (r_ratio * i)) // 256
        ng = int(g1 + (g_ratio * i)) // 256
        nb = int(b1 + (b_ratio * i)) // 256
        color = f"#{nr:02x}{ng:02x}{nb:02x}"
        canvas.create_line(0, i, width, i, fill=color)

root = tk.Tk()
root.geometry("400x300")

canvas = tk.Canvas(root, width=400, height=300)
canvas.pack(fill="both", expand=True)

draw_gradient(canvas, "#1e3c72", "#2a5298")  # azul degradado
root.mainloop()
