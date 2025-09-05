import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from typing import Callable
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- DIÁLOGOS EMERGENTES ---

class DialogoBase(tk.Toplevel):
    """
    Clase base para todas las ventanas de diálogo.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.resultado = None
        self.iconbitmap("favicon.ico")

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
    """
    Diálogo para solicitar dimensiones de una imagen RAW.
    """
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
    """
    Plantilla base para ventanas de herramientas con parámetros.
    """
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
    """
    Diálogo para introducir el valor de Gamma y realizar la transformación.
    """
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
    """
    Dialogo para umbralizar una imágen.
    """
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

class DialogoHistogramas(DialogoBase):
    """
    Dialogo para mostrar los histogramas RGB y escala de grises.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent)
        self.app = app_principal
        self.title("Histogramas de la Imagen")

        datos = self.app._tomar_niveles_grisrgb_aplanados()

        fig = Figure(figsize=(9, 7), dpi=100)
        ((ax1, ax2), (ax3, ax4)) = fig.subplots(2, 2)
        
        fig.suptitle('Histogramas de Canales de Color y Niveles de Gris', fontsize=14)

        # gris
        ax1.hist(datos['gris'], bins=256, range=[0, 256], color='gray', density=True)
        ax1.set_title("Niveles de Gris")

        # r
        ax2.hist(datos['rojo'], bins=256, range=[0, 256], color='red', density=True)
        ax2.set_title("Canal Rojo")

        # g
        ax3.hist(datos['verde'], bins=256, range=[0, 256], color='green', density=True)
        ax3.set_title("Canal Verde")

        # b
        ax4.hist(datos['azul'], bins=256, range=[0, 256], color='blue', density=True)
        ax4.set_title("Canal Azul")
        
        fig.tight_layout(rect=[0, 0.03, 1, 0.95]) # rect ajusta para el suptitle

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=5)
        self._finalizar_y_posicionar()

class DialogoHistogramaDist(DialogoBase):
    """
    Clase base para diálogos que grafican histogramas de distribuciones de forma interactiva.
    """
    def __init__(self, parent, app_principal, titulo, param_label, distribucion):
        super().__init__(parent)
        self.app = app_principal
        self.title(titulo)

        self.distribucion = distribucion
        self.intensidad = tk.StringVar(value="25")
        self.num_muestras = 10000

        self.X_LIM = (-200, 200) # Límite para el eje X (valores generados)
        self.Y_LIM = (0, 0.1)  # Límite para el eje Y (densidad)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame_slider = ttk.Frame(self)
        ttk.Label(frame_slider, text=param_label).pack(side=tk.LEFT, padx=5)
        tk.Scale(
            frame_slider,
            from_=1, to=100,
            orient="horizontal",
            variable=self.intensidad,
            resolution=1,
            showvalue=True,
            length=350,
            command=self._actualizar_grafico
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        frame_slider.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=5)
        
        self._finalizar_y_posicionar()
        self._actualizar_grafico()

    def _actualizar_grafico(self, *args):
        intensidad = int(self.intensidad.get())
        
        vector_resultante = self.app._generar_vector_ruido(self.distribucion, intensidad, self.num_muestras
        )
        
        # Borra y redibuja el histograma
        self.ax.clear()
        self.ax.hist(vector_resultante, bins=100, density=True)
        self.ax.set_xlim(self.X_LIM)
        self.ax.set_ylim(self.Y_LIM)
        self.ax.set_title(f"Histograma de Densidad (Intensidad = {intensidad})")
        self.ax.set_xlabel("Valor")
        self.ax.set_ylabel("Densidad")
        self.ax.grid(True, linestyle='--')
        self.fig.tight_layout()
        
        self.canvas.draw()

class DialogoHistogramaGaussiano(DialogoHistogramaDist):
    """
    Diálogo específico para histograma Gaussiano.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Histograma Gaussiano", "Desviación Estándar (σ):", np.random.normal)

class DialogoHistogramaRayleigh(DialogoHistogramaDist):
    """
    Diálogo específico para histograma Rayleigh.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Histograma Rayleigh", "Parámetro Xi (ξ):", np.random.rayleigh)
    
class DialogoHistogramaExponencial(DialogoHistogramaDist):
    """
    Diálogo específico para histograma Exponencial.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Histograma Exponencial", "Parámetro de Escala (1/λ):", np.random.exponential)

class DialogoRuido(DialogoHerramienta):
    """
    Clase base para diálogos de ruido. Provee UI y lógica común.
    """
    def __init__(self, parent, app_principal, titulo, param_label, distribucion):
        super().__init__(parent, app_principal, titulo)
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.tipo = tk.StringVar(value="Aditivo")
        self.valor_d = tk.StringVar(value="50")
        self.intensidad = tk.IntVar(value="20")
        self.distribucion = distribucion

        ttk.Label(self.frame_herramienta, text="Porcentaje de Píxeles a Afectar (%):").pack(padx=5, pady=(10, 0))
        tk.Scale(
            self.frame_herramienta,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.valor_d,
            resolution=1,
            showvalue=True,
            length=350
            ).pack(padx=5, pady=5)

        ttk.Label(self.frame_herramienta, text="Selecciona el tipo de aplicación de ruido").pack(padx=5, pady=5)

        ttk.Radiobutton(self.frame_herramienta, text="Aditivo", variable=self.tipo, value="Aditivo").pack(padx=5, pady=5)
        ttk.Radiobutton(self.frame_herramienta, text="Multiplicativo", variable=self.tipo, value="Multiplicativo").pack(padx=5, pady=5)

        ttk.Label(self.frame_herramienta, text=param_label).pack(padx=5, pady=(10,0))

        tk.Scale(
            self.frame_herramienta,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.intensidad,
            resolution=1,
            showvalue=True,
            length=350
            ).pack(padx=5, pady=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _generar_vector_ruido(self):
        intensidad = int(self.intensidad.get())
        d = int(self.valor_d.get())

        imagen_np = np.array(self.app.imagen_procesada)

        m, n = imagen_np.shape[:2]
        num_contaminados = int((d * (m * n)) / 100)

        return self.app._generar_vector_ruido(self.distribucion, intensidad, num_contaminados)

    def _on_apply(self):
        tipo = str(self.tipo.get())
        vector_ruido = self._generar_vector_ruido()
        d = int(self.valor_d.get())
        
        self.app._aplicar_ruido(self.copia_imagen, tipo, vector_ruido, d)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoRuidoGaussiano(DialogoRuido):
    """
    Diálogo específico para ruido Gaussiano.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Ruido Gaussiano", "Desviación Estándar (σ):", np.random.normal)

class DialogoRuidoRayleigh(DialogoRuido):
    """
    Diálogo específico para ruido Rayleigh.
    """   
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Ruido Rayleigh", "Xi (ξ):", np.random.rayleigh)
    
class DialogoRuidoExponencial(DialogoRuido):
    """
    Diálogo específico para ruido Exponencial.
    """   
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Ruido Exponencial", "Lambda (λ):", np.random.exponential)

class DialogoFiltro(DialogoHerramienta):
    """
    Clase base para diálogos de filtro. Provee UI y lógica común.
    """
    def __init__(self, parent, app_principal, titulo):
        super().__init__(parent, app_principal, titulo)
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.tam_filtro = tk.StringVar(value="3")
        #self.factor = tk.StringVar(value="1")

        ttk.Label(self.frame_herramienta, text="Tamaño de mascara(impar):").pack(padx=5, pady=(10, 0))
        tk.Scale(
            self.frame_herramienta,
            from_=3,
            to=15,
            orient="horizontal",
            variable=self.tam_filtro,
            resolution=2,
            showvalue=True,
            length=200,
            command=self._actualizar_valor
            ).pack(padx=5, pady=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)
    
    def _actualizar_valor(self):
        pass

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        filtro = np.ones((k, k))
        factor = 1
        return (filtro, factor)

    def _on_apply(self):
        filtro, factor = self._obtener_filtro_y_factor()
        #print("Filtro usado:")
        #print(filtro)
        self.app._aplicar_filtro(self.copia_imagen, filtro, factor)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoFiltroMedia(DialogoFiltro):
    """
    Diálogo específico para filtro de la media.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro de la media")

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        filtro = np.ones((k, k))
        factor = 1 / np.sum(filtro)
        return (filtro, factor)
    
class DialogoFiltroGaussiano(DialogoFiltro):
    """
    Diálogo específico para filtro gaussiano.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro gaussiano")

        self.label_sigma = ttk.Label(self.frame_herramienta, text=f"Sigma correspondiente (σ): {int((int(self.tam_filtro.get())-1)/2)}")
        self.label_sigma.pack(padx=5, pady=(0, 10))

    def _actualizar_valor(self, valor):
        k = int(valor)
        sigma = int((k-1) / 2)
        self.label_sigma.config(text=f"Sigma correspondiente (σ): {sigma}")

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        filtro = np.ones((k, k)).astype(float)
        u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
        sigma = (k-1) / 2

        for x in range(k):
            for y in range(k):
                filtro[x, y] = (1 / (2 * np.pi * sigma**2)) * np.exp(-((x - u)**2 + (y - u)**2)/(2 * sigma**2))

        factor = 1 / np.sum(filtro)
        #print(f"Factor usado: {1} / {np.sum(filtro)}")
        return (filtro, factor)

class DialogoFiltroRealce(DialogoFiltro):
    """
    Diálogo específico para filtro de realce de bordes.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro de la realce de bordes")

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        filtro = -1 * np.ones((k, k))
        filtro[k//2, k//2] = k**2 - 1
        factor = 1
        return (filtro, factor)