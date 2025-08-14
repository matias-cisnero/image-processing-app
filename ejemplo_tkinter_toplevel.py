import tkinter as tk

def abrir_ventana_secundaria():
    # Crear la ventana Toplevel
    ventana_sec = tk.Toplevel(ventana)
    ventana_sec.title("Ventana de Preferencias")
    ventana_sec.geometry("300x200")
    
    # Hacerla modal (bloquea la ventana principal)
    ventana_sec.grab_set()
    # Mantenerla sobre la ventana principal
    ventana_sec.transient(ventana)

    label = tk.Label(ventana_sec, text="Esta es una ventana secundaria modal.")
    label.pack(pady=20)
    
    boton_cerrar = tk.Button(ventana_sec, text="Cerrar", command=ventana_sec.destroy)
    boton_cerrar.pack(pady=10)

# --- Ventana Principal ---
ventana = tk.Tk()
ventana.title("Ventana Principal")
ventana.geometry("500x400")

label_principal = tk.Label(ventana, text="Haz clic en el botón para abrir un diálogo.")
label_principal.pack(pady=30)

boton_abrir = tk.Button(ventana, text="Abrir Preferencias", command=abrir_ventana_secundaria)
boton_abrir.pack()

ventana.mainloop()