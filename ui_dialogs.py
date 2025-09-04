import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from typing import Callable

# --- DIÁLOGOS EMERGENTES ---

class DialogoBase(tk.Toplevel):
    """Clase base para todas las ventanas de diálogo."""
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.resultado = None

    def _finalizar_y_posicionar(self, reference_widget=None):
        """Calcula el tamaño necesario para el contenido y posiciona la ventana."""
        self.update_idletasks() # Asegura que el tamaño esté calculado
        
        # Si no se da una referencia, usa la ventana principal
        if reference_widget is None:
            reference_widget = self.master

        # Posición de la ventana de referencia
        ref_x = reference_widget.winfo_rootx()
        ref_y = reference_widget.winfo_rooty()
        
        # Offset para que no aparezca exactamente en la esquina
        offset_x = 20
        offset_y = 20
        
        # Posicionar la ventana de diálogo
        self.geometry(f'+{ref_x + offset_x}+{ref_y + offset_y}')

class DialogoDimensiones(DialogoBase):
    """Diálogo para solicitar dimensiones de una imagen RAW."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dimensiones de la Imagen RAW")

        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Ancho (width):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ancho_var = tk.StringVar()
        self.ancho_entry = ttk.Entry(frame, textvariable=self.ancho_var)
        self.ancho_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Alto (height):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.alto_var = tk.StringVar()
        self.alto_entry = ttk.Entry(frame, textvariable=self.alto_var)
        self.alto_entry.grid(row=1, column=1, padx=5, pady=5)

        boton_frame = ttk.Frame(self)
        boton_frame.pack(pady=10)
        ttk.Button(boton_frame, text="Aceptar", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(boton_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.ancho_entry.focus_set()

        # --- Posicionar al final ---
        self._finalizar_y_posicionar()
        self.wait_window(self)

    def _on_ok(self):
        try:
            ancho = int(self.ancho_var.get())
            alto = int(self.alto_var.get())
            if ancho <= 0 or alto <= 0: raise ValueError("Las dimensiones deben ser positivas.")
            self.resultado = (ancho, alto)
            self.destroy()
        except (ValueError, TypeError):
            messagebox.showerror("Error de Entrada", "Por favor, ingrese números enteros válidos y positivos.", parent=self)

class DialogoResultado(DialogoBase):
    def __init__(self, parent, imagen_pil: Image.Image, titulo: str, guardar_callback: Callable):
        super().__init__(parent)
        self.title(titulo)
        img_tk = ImageTk.PhotoImage(imagen_pil)
        label_imagen = ttk.Label(self, image=img_tk)
        label_imagen.image_ref = img_tk
        label_imagen.pack(padx=10, pady=10)
        
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=5, padx=10, fill=tk.X)
        ttk.Button(frame_botones, text="Guardar...", command=guardar_callback).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(frame_botones, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT, expand=True, padx=5)
        self._finalizar_y_posicionar()
        self.wait_window(self)

class DialogoHerramienta(DialogoBase):
    """Plantilla base para ventanas de herramientas con parámetros."""
    def __init__(self, parent, app_principal, titulo: str):
        super().__init__(parent)
        self.app = app_principal
        self.title(titulo)
        
        self.frame_herramienta = ttk.Frame(self, padding=10)
        self.frame_herramienta.pack(expand=True, fill=tk.BOTH)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10)
        ttk.Button(frame_botones, text="Aplicar", command=self._on_apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_apply(self):
        self.destroy()

    def _on_cancel(self):
        self.destroy()

class DialogoGamma(DialogoHerramienta):
    """Diálogo para introducir el valor de Gamma y realizar la transformación."""
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Transformación Gamma")
        
        self.valor_gamma = tk.StringVar(value="1.0")
        self.copia_imagen = self.app.imagen_procesada.copy()

        tk.Scale(
            self.frame_herramienta,
            from_=0,
            to=2.0,
            orient="horizontal",
            variable=self.valor_gamma,
            resolution=0.1,
            showvalue=True,
            length=200,
            command=lambda value: self.app._aplicar_gamma(self.copia_imagen, float(value))
            ).pack(padx=5, pady=5)
        
        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        gamma = float(self.valor_gamma.get())
        self.app._aplicar_gamma(self.copia_imagen, gamma)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoUmbralizacion(DialogoHerramienta):
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Umbralización")
        
        self.valor_umbral = tk.StringVar(value="128")
        self.copia_imagen = self.app.imagen_procesada.copy()

        tk.Scale(
            self.frame_herramienta,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.valor_umbral,
            resolution=1,
            showvalue=True,
            length=350,
            command=lambda value: self.app._aplicar_umbralizacion(self.copia_imagen, float(value))
            ).pack(padx=5, pady=5)
        
        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        gamma = float(self.valor_umbral.get())
        self.app._aplicar_umbralizacion(self.copia_imagen, gamma)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoNumerosAleatorios(DialogoBase):
    """Dialogo para mostrar el histograma de números aleatorios"""
    def __init__(self, parent, app_principal, titulo: str):
        super().__init__(parent)
        self.app = app_principal
        self.title(titulo)
        
        self.frame_herramienta = ttk.Frame(self, padding=10)
        self.frame_herramienta.pack(expand=True, fill=tk.BOTH)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10)
        ttk.Button(frame_botones, text="Aplicar", command=self._on_apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        self.destroy()

    def _on_cancel(self):
        self.destroy()
