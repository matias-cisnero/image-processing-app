from tkinter import Tk, Label
from PIL import Image, ImageTk

root = Tk()
root.geometry("400x300")

img = Image.new("RGB", (400, 300), "#000")
for y in range(300):
    r = int(30 + (150 - 30) * (y/300))
    g = int(60 + (200 - 60) * (y/300))
    b = int(100 + (255 - 100) * (y/300))
    for x in range(400):
        img.putpixel((x, y), (r, g, b))

bg = ImageTk.PhotoImage(img)
lbl = Label(root, image=bg)
lbl.place(x=0, y=0, relwidth=1, relheight=1)

root.mainloop()
