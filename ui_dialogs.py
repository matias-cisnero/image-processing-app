import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
    Diálogo para mostrar y descargar los histogramas RGB y de escala de grises.
    Permite guardar el gráfico completo o solo el de escala de grises.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent)
        self.app = app_principal
        self.title("Histogramas de la Imagen")

        # Pide los datos a la aplicación principal
        datos = self.app._tomar_niveles_grisrgb_aplanados()

        # Guarda la figura y los ejes como atributos de la instancia
        self.fig = Figure(figsize=(9, 7), dpi=100)
        ((self.ax_gris, self.ax_rojo), (self.ax_verde, self.ax_azul)) = self.fig.subplots(2, 2)
        
        self.fig.suptitle('Histogramas de Canales de Color y Niveles de Gris', fontsize=14)

        # Dibuja los 4 histogramas
        self.ax_gris.hist(datos['gris'], bins=256, range=[0, 256], color='gray', density=True)
        self.ax_gris.set_title("Niveles de Gris")
        self.ax_gris.grid(True, linestyle='--')

        self.ax_rojo.hist(datos['rojo'], bins=256, range=[0, 256], color='red', density=True)
        self.ax_rojo.set_title("Canal Rojo")
        self.ax_rojo.grid(True, linestyle='--')

        self.ax_verde.hist(datos['verde'], bins=256, range=[0, 256], color='green', density=True)
        self.ax_verde.set_title("Canal Verde")
        self.ax_verde.grid(True, linestyle='--')

        self.ax_azul.hist(datos['azul'], bins=256, range=[0, 256], color='blue', density=True)
        self.ax_azul.set_title("Canal Azul")
        self.ax_azul.grid(True, linestyle='--')
        
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Inserta el gráfico en la ventana de Tkinter
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Interfaz de Botones ---
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=5)
        
        ttk.Button(frame_botones, text="Guardar Todo...", command=self._guardar_grafico_completo).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Guardar solo Gris...", command=self._guardar_grafico_gris).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cerrar", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self._finalizar_y_posicionar()

    # --- Lógica de Guardado ---

    def _obtener_ruta_guardado(self):
        """Función de ayuda que abre el diálogo 'Guardar como...' y devuelve una ruta."""
        return filedialog.asksaveasfilename(
            parent=self,
            title="Guardar gráfico como...",
            defaultextension=".png",
            filetypes=[("Archivo PNG", "*.png"), ("Archivo JPG", "*.jpg")]
        )

    def _guardar_grafico_completo(self):
        """Guarda la figura completa con los 4 histogramas."""
        ruta_archivo = self._obtener_ruta_guardado()
        if ruta_archivo:
            try:
                self.fig.savefig(ruta_archivo, dpi=150)
                messagebox.showinfo("Guardado Exitoso", f"Gráfico guardado en:\n{ruta_archivo}", parent=self)
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el gráfico.\nError: {e}", parent=self)

    def _guardar_grafico_gris(self):
        """Guarda únicamente el área del subplot de niveles de gris."""
        ruta_archivo = self._obtener_ruta_guardado()
        if ruta_archivo:
            try:
                # Obtenemos el "cuadro delimitador" del subplot de grises
                bbox = self.ax_gris.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                
                # Le decimos a savefig que guarde solo lo que está dentro de ese cuadro
                self.fig.savefig(ruta_archivo, dpi=150, bbox_inches=bbox)
                messagebox.showinfo("Guardado Exitoso", f"Gráfico guardado en:\n{ruta_archivo}", parent=self)
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el gráfico.\nError: {e}", parent=self)

class DialogoHistogramaDist(DialogoBase):
    """
    Clase base para diálogos que grafican histogramas de distribuciones de forma interactiva.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent)
        self.config = config

        self.app = app_principal
        self.title(self.config['titulo'])

        self.intensidad = tk.StringVar(value="25")
        self.num_muestras = 10000

        self.X_LIM = (-200, 200) # Límite para el eje X (valores generados)
        self.Y_LIM = (0, 0.1)  # Límite para el eje Y (densidad)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame_slider = ttk.Frame(self)
        ttk.Label(frame_slider, text=self.config['param_label']).pack(side=tk.LEFT, padx=5)
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
        
        vector_resultante = self.app._generar_vector_ruido(
            distribucion = self.config['distribucion'],
            intensidad = intensidad,
            cantidad = self.num_muestras
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

class DialogoRuido(DialogoHerramienta):
    """
    Clase base para diálogos de ruido. Provee UI y lógica común.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent, app_principal, config['titulo'])
        self.config = config
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.tipo = tk.StringVar(value="Aditivo")
        self.valor_d = tk.StringVar(value="20")
        self.intensidad = tk.IntVar(value="10")
        self.sal_y_pimienta = config['sal_y_pimienta']

        ttk.Label(self.frame_herramienta, text="Porcentaje de Píxeles a Afectar (%):").pack(padx=5, pady=(10, 0))
        tk.Scale(
            self.frame_herramienta,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.valor_d,
            resolution=config['res'],
            showvalue=True,
            length=350
            ).pack(padx=5, pady=5)

        if not self.sal_y_pimienta:
            ttk.Label(self.frame_herramienta, text="Selecciona el tipo de aplicación de ruido").pack(padx=5, pady=5)

            ttk.Radiobutton(self.frame_herramienta, text="Aditivo", variable=self.tipo, value="Aditivo").pack(padx=5, pady=5)
            ttk.Radiobutton(self.frame_herramienta, text="Multiplicativo", variable=self.tipo, value="Multiplicativo").pack(padx=5, pady=5)

            ttk.Label(self.frame_herramienta, text=self.config['param_label']).pack(padx=5, pady=(10,0))

            tk.Scale(
                self.frame_herramienta,
                from_=0,
                to=50,
                orient="horizontal",
                variable=self.intensidad,
                resolution=1,
                showvalue=True,
                length=350
                ).pack(padx=5, pady=5)
        else:
            ttk.Label(self.frame_herramienta, text="p = (porcentaje / 2) / 100").pack(padx=5, pady=(10, 0))

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        if not self.sal_y_pimienta:
            d = int(self.valor_d.get())
            intensidad = int(self.intensidad.get())
            tipo = str(self.tipo.get())

            imagen_np = np.array(self.app.imagen_procesada)
            m, n = imagen_np.shape[:2]
            num_contaminados = int((d * (m * n)) / 100)

            vector_ruido = self.app._generar_vector_ruido(
                distribucion=self.config['distribucion'],
                intensidad=intensidad,
                cantidad=num_contaminados
            )

            if vector_ruido.size > 0:
                self.app._aplicar_ruido(self.copia_imagen, tipo, vector_ruido, d)
        else:
            d = int(self.valor_d.get()) / 2
            p = d / 100
        
            self.app._aplicar_ruido_sal_y_pimienta(self.copia_imagen, p)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoFiltro(DialogoHerramienta):
    """
    Clase base para diálogos de filtro. Provee UI y lógica común.
    """
    def __init__(self, parent, app_principal, titulo):
        super().__init__(parent, app_principal, titulo)
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.tam_filtro = tk.StringVar(value="3")
        #self.factor = tk.StringVar(value="1")

        ttk.Label(self.frame_herramienta, text="Tamaño de mascara (k):").pack(padx=5, pady=(10, 0))
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
    
    def _actualizar_valor(self, valor):
        pass

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        filtro = np.ones((k, k)).astype(int)
        factor = 1
        return (filtro, factor)

    def _on_apply(self):
        filtro, factor = self._obtener_filtro_y_factor()
        print("Filtro usado:")
        print(filtro)
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
        return self.app._filtro_media(k)
    
class DialogoFiltroMediana(DialogoFiltro):
    """
    Diálogo específico para filtro de la mediana.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro de la mediana")
    
    def _on_apply(self):
        filtro, _ = self._obtener_filtro_y_factor()
        print("Filtro usado:")
        print(filtro)
        self.app._aplicar_filtro_mediana(self.copia_imagen, filtro)
        self.destroy()

class DialogoFiltroMedianaPonderada(DialogoFiltro):
    """
    Diálogo específico para filtro de la mediana ponderada.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro de la mediana ponderada")

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        return self.app._filtro_mediana_ponderada(k)
    
    def _on_apply(self):
        filtro, _ = self._obtener_filtro_y_factor()
        print("Filtro usado:")
        print(filtro)
        self.app._aplicar_filtro_mediana(self.copia_imagen, filtro)
        self.destroy()
    
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
        return self.app._filtro_gaussiano(k)

class DialogoFiltroRealce(DialogoFiltro):
    """
    Diálogo específico para filtro de realce de bordes.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro de la realce de bordes")

    def _obtener_filtro_y_factor(self):
        k = int(self.tam_filtro.get())
        return self.app._filtro_realce(k)