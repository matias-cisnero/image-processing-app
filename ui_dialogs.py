import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from typing import Callable
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from processing import (aplicar_gamma, aplicar_umbralizacion, generar_vector_ruido, aplicar_ruido, aplicar_ruido_sal_y_pimienta,
                        aplicar_filtro, aplicar_filtro_isotropico, aplicar_metodo_del_laplaciano)

# --- TOOLTIP ---

class Tooltip:
    """
    Crea una etiqueta de ayuda emergente (tooltip) para cualquier widget de Tkinter.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # --- CORRECCIÓN AQUÍ ---
        # Se reemplaza 'padding' por 'padx' y 'pady'.
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            padx=5, # Padding horizontal
            pady=3  # Padding vertical
        )
        label.pack()

    def hide_tip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

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

class DialogoRecorteConAnalisis(DialogoBase):
    """
    Un diálogo que muestra una imagen, sus datos de análisis y botones.
    """
    def __init__(self, parent, titulo: str, imagen_pil: Image.Image, datos_analisis: dict, guardar_callback: Callable):
        super().__init__(parent)
        self.title(titulo)

        # --- Parte de la Imagen ---
        img_tk = ImageTk.PhotoImage(imagen_pil)
        label_imagen = ttk.Label(self, image=img_tk)
        label_imagen.image_ref = img_tk # Guarda la referencia
        label_imagen.pack(padx=10, pady=10)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=5, padx=10)

        # --- Parte del Análisis ---
        frame_analisis = ttk.Labelframe(self, text="Análisis de la Región", padding=10)
        frame_analisis.pack(padx=10, pady=5, fill="x")
        frame_analisis.columnconfigure(1, weight=1)

        # Crea las filas de la tabla de análisis a partir del diccionario
        row_counter = 0
        for clave, valor in datos_analisis.items():
            ttk.Label(frame_analisis, text=f"{clave}:").grid(row=row_counter, column=0, sticky="w")
            ttk.Label(frame_analisis, text=valor, anchor="e").grid(row=row_counter, column=1, sticky="ew")
            row_counter += 1
            
        # --- Parte de los Botones ---
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10, padx=10, fill=tk.X)
        ttk.Button(frame_botones, text="Guardar Recorte...", command=guardar_callback).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(frame_botones, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT, expand=True, padx=5)
        
        self.resizable(False, False)
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
            command=lambda value: self.app._aplicar_transformacion(self.copia_imagen, aplicar_gamma, gamma=float(value))
            ).pack(padx=5, pady=5)
        
        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        gamma = float(self.valor_gamma.get())
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_gamma, gamma=gamma)
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
            command=lambda value: self.app._aplicar_transformacion(self.copia_imagen, aplicar_umbralizacion, float(value))
            ).pack(padx=5, pady=5)
        
        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        umbral = float(self.valor_umbral.get())
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_umbralizacion, umbral=umbral)
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
        
        vector_resultante = generar_vector_ruido(
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
        self.intensidad = tk.StringVar(value="10")
        self.sal_y_pimienta = config['sal_y_pimienta']

        frame_principal = self.frame_herramienta
        frame_principal.columnconfigure(1, weight=1)

        grupo_general = ttk.LabelFrame(frame_principal, text="Parámetros Generales", padding=10)
        grupo_general.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        grupo_general.columnconfigure(1, weight=1)

        ttk.Label(grupo_general, text="Píxeles a Afectar (%):").grid(row=0, column=0, sticky="w", pady=5)
        tk.Scale(
            grupo_general,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.valor_d,
            resolution=config['res'],
            showvalue=True#,
            #length=250
            ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        

        if not self.sal_y_pimienta:
            grupo_especifico = ttk.Labelframe(frame_principal, text="Parámetros Específicos", padding=10)
            grupo_especifico.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            grupo_especifico.columnconfigure(1, weight=1)

            ttk.Label(grupo_general, text="Tipo de Aplicación:").grid(row=1, column=0, sticky="w", pady=5)

            frame_radios = ttk.Frame(grupo_general)
            ttk.Radiobutton(frame_radios, text="Aditivo", variable=self.tipo, value="Aditivo").pack(side="left", padx=5)
            ttk.Radiobutton(frame_radios, text="Multiplicativo", variable=self.tipo, value="Multiplicativo").pack(side="left", padx=5)
            frame_radios.grid(row=1, column=1, sticky="w", pady=5)

            ttk.Label(grupo_especifico, text=self.config['param_label']).grid(row=0, column=0, sticky="w", pady=5)

            tk.Scale(
                grupo_especifico,
                from_=0,
                to=50,
                orient="horizontal",
                variable=self.intensidad,
                resolution=1,
                showvalue=True#,
                #length=250
                ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        else:
            ttk.Label(grupo_general, text="p = (porcentaje / 2) / 100").grid(row=1, column=0, columnspan=2)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        if not self.sal_y_pimienta:
            d = int(self.valor_d.get())
            intensidad = int(self.intensidad.get())
            tipo = str(self.tipo.get())

            imagen_np = np.array(self.app.imagen_procesada)
            m, n = imagen_np.shape[:2]
            num_contaminados = int((d * (m * n)) / 100)

            vector_ruido = generar_vector_ruido(
                distribucion=self.config['distribucion'],
                intensidad=intensidad,
                cantidad=num_contaminados
            )

            if vector_ruido.size > 0:
                self.app._aplicar_transformacion(self.copia_imagen, aplicar_ruido, tipo=tipo, vector_ruido=vector_ruido, d=d)
        else:
            d = int(self.valor_d.get()) / 2
            p = d / 100

            self.app._aplicar_transformacion(self.copia_imagen, aplicar_ruido_sal_y_pimienta, p=p)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoFiltro(DialogoHerramienta):
    """
    Clase base para diálogos de filtro. Provee UI y lógica común.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent, app_principal, config['titulo'])
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        #self.factor = tk.StringVar(value="1")
        self.gaussiano = config['gaussiano']
        self.func_filtro = config['filtro']
        self.modo = config['modo']
        self.mediana = config['mediana']

        valor = "1" if self.gaussiano else "3"
        self.tam_filtro = tk.StringVar(value=valor)
        self.param_label = "Desviación Estándar (σ):" if self.gaussiano else "Tamaño de máscara (k):"
        self.inicio = 1 if self.gaussiano else 3
        self.resolution = 1 if self.gaussiano else 2

        ttk.Label(self.frame_herramienta, text=self.param_label).pack(padx=5, pady=(10, 0))
        tk.Scale(
            self.frame_herramienta,
            from_=self.inicio,
            to=15,
            orient="horizontal",
            variable=self.tam_filtro,
            resolution=self.resolution,
            showvalue=True,
            length=200,
            command=self._actualizar_valor
            ).pack(padx=5, pady=5)

        if self.gaussiano:
            self.label_sigma = ttk.Label(self.frame_herramienta, text=f"Tamaño de máscara correspondiente (k): {int((int(self.tam_filtro.get())*2)+1)}")
            self.label_sigma.pack(padx=5, pady=(0, 10))

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)
    
    def _actualizar_valor(self, valor):
        if self.gaussiano:
            sigma = int(valor)
            k = int(2 * sigma + 1)
            self.label_sigma.config(text=f"Tamaño de máscara correspondiente (k): {k}")

    def _on_apply(self):
        k = int(self.tam_filtro.get())
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_filtro, func_filtro=self.func_filtro, k=k, modo=self.modo, mediana=self.mediana)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoDifusion(DialogoHerramienta):
    """
    Clase base para diálogos de difusión.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent, app_principal, config['titulo'])
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.isotropico = config['isotropico']

        self.valor = tk.StringVar(value=1)
        self.param_label = "Tiempo (t):" if self.isotropico else "TDesviación Estándar (σ):"

        ttk.Label(self.frame_herramienta, text=self.param_label).pack(padx=5, pady=(10, 0))
        tk.Scale(
            self.frame_herramienta,
            from_=1,
            to=15,
            orient="horizontal",
            variable=self.valor,
            resolution=1,
            showvalue=True,
            length=200
            ).pack(padx=5, pady=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _on_apply(self):
        t = int(self.valor.get())
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_filtro_isotropico, t=t)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoLaplaciano(DialogoHerramienta):
    """
    Diálogo para aplicar el filtro Laplaciano con o sin evaluación de la pendiente.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent, app_principal, config['titulo'])
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.usar_pendiente = tk.BooleanVar(value=False)
        self.umbral_pendiente = tk.IntVar(value=50)

        self.sigma = tk.IntVar(value=1)
        self.log = config['log']

        grupo_opciones = ttk.Labelframe(self.frame_herramienta, text="Opciones", padding=10)
        grupo_opciones.pack(fill="x", padx=10, pady=5, expand=True)


        if self.log:
            ttk.Label(grupo_opciones, text="Desviación Estándar (σ):").pack(padx=5, pady=(10, 0))
            tk.Scale(
                grupo_opciones,
                from_=1,
                to=100,
                orient="horizontal",
                variable=self.sigma,
                resolution=1,
                showvalue=True,
                length=300,
                command=self._actualizar_valor
            ).pack(fill="x", expand=True, pady=5)
            self.label_sigma = ttk.Label(grupo_opciones, text=f"Tamaño de máscara correspondiente (k): {int((int(self.sigma.get())*4)+1)}")
            self.label_sigma.pack(padx=5, pady=(0, 10))

        check_pendiente = ttk.Checkbutton(
            grupo_opciones,
            text="Usar Evaluación de la Pendiente (con umbral)",
            variable=self.usar_pendiente,
            command=self._toggle_umbral_slider
        )
        check_pendiente.pack(anchor="w", pady=5)

        self.frame_umbral = ttk.Frame(grupo_opciones)

        ttk.Label(self.frame_umbral, text="Umbral:").pack(anchor="w", pady=(10, 0))
        tk.Scale(
            self.frame_umbral,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.umbral_pendiente,
            resolution=1,
            showvalue=True,
            length=300
        ).pack(fill="x", expand=True, pady=5)
        
        self._toggle_umbral_slider()
        
        self._finalizar_y_posicionar()

    def _toggle_umbral_slider(self):
        """Muestra u oculta el slider del umbral según el estado del checkbox."""
        if self.usar_pendiente.get():
            self.frame_umbral.pack(fill="x", expand=True, pady=5)
        else:
            self.frame_umbral.pack_forget()
    
    def _actualizar_valor(self, valor):
        if self.log:
            sigma = int(valor)
            k = int(4 * sigma + 1)
            self.label_sigma.config(text=f"Tamaño de máscara correspondiente (k): {k}")

    def _on_apply(self):
        pendiente = self.usar_pendiente.get()
        umbral = self.umbral_pendiente.get()
        sigma = self.sigma.get()
        log = self.log
        
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_metodo_del_laplaciano, log=log, pendiente=pendiente, umbral=umbral, sigma=sigma)
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()