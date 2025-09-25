import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("400x300")
root.attributes("-alpha", 0.9)  # transparencia 90%
root.title("Ventana con transparencia")

label = ctk.CTkLabel(root, text="Hola Matías 😎", font=("Segoe UI", 18))
label.pack(pady=40)

root.mainloop()
