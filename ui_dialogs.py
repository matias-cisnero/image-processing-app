import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from typing import Callable
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from processing import (aplicar_gamma, aplicar_umbralizacion, generar_vector_ruido, aplicar_ruido, aplicar_ruido_sal_y_pimienta,
                        aplicar_filtro, aplicar_metodo_del_laplaciano, aplicar_filtro_difusion, aplicar_filtro_bilateral,
                        aplicar_detector_canny
                        )

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

        self.icono_aceptar = tk.PhotoImage(file="icons/ui_aceptar.png").subsample(4,4)
        self.icono_cancelar = tk.PhotoImage(file="icons/ui_cancelar.png").subsample(4,4)
        
        self.frame_herramienta = ttk.Frame(self, padding=10)
        self.frame_herramienta.pack(expand=True, fill=tk.BOTH)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10)
        btn_aceptar = ttk.Button(frame_botones, command=self._on_apply, image=self.icono_aceptar)
        btn_aceptar.pack(side=tk.LEFT, padx=5)
        Tooltip(widget=btn_aceptar, text="Aplicar")
        btn_cancelar = ttk.Button(frame_botones, command=self._on_cancel, image=self.icono_cancelar)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        Tooltip(widget=btn_cancelar, text="Cancelar")
        
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

        self.valor_gamma = tk.DoubleVar(value=1.0)
        self.copia_imagen = self.app.imagen_procesada.copy()

        # Frame principal con título
        label_parametros = ttk.Labelframe(self.frame_herramienta, text="Gamma", padding=10)
        label_parametros.pack(fill="x", padx=10, pady=5, expand=True)

        # Label del valor a la izquierda
        lbl_valor = ttk.Label(label_parametros, text=f"{self.valor_gamma.get():.1f}", width=4)
        lbl_valor.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Scale de ttk
        scale_gamma = ttk.Scale(
            label_parametros,
            from_=0.0,
            to=2.0,
            orient="horizontal",
            variable=self.valor_gamma,
            command=lambda value: self._actualizar_gamma(value, lbl_valor)
        )
        scale_gamma.grid(row=0, column=1, sticky="ew")
        label_parametros.columnconfigure(1, weight=1)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _actualizar_gamma(self, value, label):
        valor = float(value)
        label.config(text=f"{valor:.1f}")
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_gamma, gamma=valor)

    def _on_apply(self):
        gamma = float(self.valor_gamma.get())
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_gamma, gamma=gamma)
        self.destroy()

    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoUmbralizacion(DialogoHerramienta):
    """
    Diálogo para umbralizar una imagen.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Umbralización")
        
        self.valor_umbral = tk.DoubleVar(value=128.0)
        self.copia_imagen = self.app.imagen_procesada.copy()

        # Frame principal con título
        label_parametros = ttk.Labelframe(self.frame_herramienta, text="Umbral", padding=10)
        label_parametros.pack(fill="x", padx=10, pady=5, expand=True)

        # Label que muestra el valor actual
        lbl_valor = ttk.Label(label_parametros, text=f"{self.valor_umbral.get():.0f}", width=4)
        lbl_valor.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Scale de ttk
        scale_umbral = ttk.Scale(
            label_parametros,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.valor_umbral,
            command=lambda value: self._actualizar_umbral(value, lbl_valor)
        )
        scale_umbral.grid(row=0, column=1, sticky="ew")
        label_parametros.columnconfigure(1, weight=1)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    def _actualizar_umbral(self, value, label):
        """Actualiza el label y aplica la transformación mientras se mueve el slider."""
        valor = round(float(value))
        label.config(text=str(valor))
        self.app._aplicar_transformacion(self.copia_imagen, aplicar_umbralizacion, umbral=valor)

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
        self.valor_d = tk.DoubleVar(value=20.0)
        self.intensidad = tk.DoubleVar(value=10.0)
        self.sal_y_pimienta = config['sal_y_pimienta']

        frame_principal = self.frame_herramienta
        frame_principal.columnconfigure(1, weight=1)

        # ----- GRUPO GENERAL -----
        grupo_general = ttk.LabelFrame(frame_principal, text="Parámetros Generales", padding=10)
        grupo_general.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        grupo_general.columnconfigure(1, weight=1)

        # Etiqueta y Scale para % de píxeles afectados
        ttk.Label(grupo_general, text="Píxeles a Afectar (%):").grid(row=0, column=0, sticky="w", pady=5)
        self.lbl_valor_d = ttk.Label(grupo_general, text=f"{int(self.valor_d.get())}", width=4)
        self.lbl_valor_d.grid(row=0, column=2, padx=(5, 0), sticky="e")

        ttk.Scale(
            grupo_general,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.valor_d,
            command=lambda v: self.lbl_valor_d.config(text=f"{float(v):.0f}")
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # ----- SI NO ES SAL Y PIMIENTA -----
        if not self.sal_y_pimienta:
            grupo_especifico = ttk.Labelframe(frame_principal, text="Parámetros Específicos", padding=10)
            grupo_especifico.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            grupo_especifico.columnconfigure(1, weight=1)

            # Tipo de aplicación
            ttk.Label(grupo_especifico, text="Tipo de Aplicación:").grid(row=0, column=0, sticky="w", pady=5)
            frame_radios = ttk.Frame(grupo_especifico)
            ttk.Radiobutton(frame_radios, text="Aditivo", variable=self.tipo, value="Aditivo").pack(side="left", padx=5)
            ttk.Radiobutton(frame_radios, text="Multiplicativo", variable=self.tipo, value="Multiplicativo").pack(side="left", padx=5)
            frame_radios.grid(row=0, column=1, sticky="w", pady=5)

            # Parámetro de intensidad
            ttk.Label(grupo_especifico, text=self.config['param_label']).grid(row=1, column=0, sticky="w", pady=5)
            self.lbl_intensidad = ttk.Label(grupo_especifico, text=f"{int(self.intensidad.get())}", width=4)
            self.lbl_intensidad.grid(row=1, column=2, padx=(5, 0), sticky="e")

            ttk.Scale(
                grupo_especifico,
                from_=0,
                to=50,
                orient="horizontal",
                variable=self.intensidad,
                command=lambda v: self.lbl_intensidad.config(text=f"{float(v):.0f}")
            ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # ----- SI ES SAL Y PIMIENTA -----
        else:
            ttk.Label(grupo_general, text="p = (porcentaje / 2) / 100").grid(row=1, column=0, columnspan=3, pady=(5, 0))

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    # ----- APLICAR -----
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
                self.app._aplicar_transformacion(
                    self.copia_imagen, 
                    aplicar_ruido, 
                    tipo=tipo, 
                    vector_ruido=vector_ruido, 
                    d=d
                )
        else:
            d = int(self.valor_d.get()) / 2
            p = d / 100
            self.app._aplicar_transformacion(self.copia_imagen, aplicar_ruido_sal_y_pimienta, p=p)
        self.destroy()
    
    # ----- CANCELAR -----
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
        self.gaussiano = config['gaussiano']
        self.func_filtro = config['filtro']
        self.modo = config['modo']
        self.mediana = config['mediana']

        # Valores iniciales según tipo
        valor_inicial = 1 if self.gaussiano else 3
        self.tam_filtro = tk.DoubleVar(value=valor_inicial)
        self.param_label = "Desviación Estándar (σ):" if self.gaussiano else "Tamaño de máscara (k):"
        self.inicio = 1 if self.gaussiano else 3

        label_parametros = ttk.Labelframe(self.frame_herramienta, text=self.param_label, padding=10)
        label_parametros.pack(fill="x", padx=10, pady=5, expand=True)

        # Label del valor a la izquierda
        self.lbl_valor = ttk.Label(label_parametros, text=f"{int(self.tam_filtro.get())}", width=4)
        self.lbl_valor.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Slider (usa escala continua, pero ajustamos manualmente a valores impares)
        self.scale = ttk.Scale(
            label_parametros,
            from_=self.inicio,
            to=15,
            orient="horizontal",
            variable=self.tam_filtro,
            command=self._actualizar_valor
        )
        self.scale.grid(row=0, column=1, sticky="ew")
        label_parametros.columnconfigure(1, weight=1)

        # Label auxiliar para mostrar tamaño de máscara si es gaussiano
        if self.gaussiano:
            k = int(2 * self.tam_filtro.get() + 1)
            self.label_sigma = ttk.Label(label_parametros, text=f"Tamaño de máscara correspondiente (k): {k}")
            self.label_sigma.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)
    
    def _actualizar_valor(self, valor):
        """Actualiza el label y asegura valores impares o consistentes según tipo."""
        val = float(valor)
        if self.gaussiano:
            sigma = int(round(val))
            k = int(2 * sigma + 1)
            self.lbl_valor.config(text=str(sigma))
            self.label_sigma.config(text=f"Tamaño de máscara correspondiente (k): {k}")
        else:
            # Forzamos que sea impar
            k = int(round(val))
            if k % 2 == 0:
                k += 1 if k < 15 else -1  # mantiene dentro del rango
            self.tam_filtro.set(k)
            self.lbl_valor.config(text=str(k))

    def _on_apply(self):
        """Aplica el filtro solo al confirmar."""
        if self.gaussiano:
            sigma = int(self.tam_filtro.get())
            k = int(2 * sigma + 1)
        else:
            k = int(self.tam_filtro.get())
        self.app._aplicar_transformacion(
            self.copia_imagen,
            aplicar_filtro,
            func_filtro=self.func_filtro,
            k=k,
            modo=self.modo,
            mediana=self.mediana
        )
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy()

class DialogoDifusion(DialogoHerramienta):
    """
    Diálogo para aplicar difusión isotrópica o anisotrópica a una imagen.
    """
    def __init__(self, parent, app_principal, config):
        super().__init__(parent, app_principal, config['titulo'])
        
        self.copia_imagen = self.app.imagen_procesada.copy()
        self.isotropico = config['isotropico']

        self.t = tk.DoubleVar(value=1.0)
        self.sigma = tk.DoubleVar(value=1.0)

        # --- Labelframe principal ---
        label_parametros = ttk.Labelframe(self.frame_herramienta, text="Parámetros", padding=10)
        label_parametros.pack(fill="x", padx=10, pady=5, expand=True)
        label_parametros.columnconfigure(1, weight=1)

        # --- Tiempo (t) ---
        ttk.Label(label_parametros, text="Tiempo (t):").grid(row=0, column=0, sticky="w", pady=(0, 3))
        lbl_t_valor = ttk.Label(label_parametros, text=f"{self.t.get():.0f}", width=4)
        lbl_t_valor.grid(row=0, column=2, sticky="e", padx=(10, 0))

        scale_t = ttk.Scale(
            label_parametros,
            from_=1,
            to=15,
            orient="horizontal",
            variable=self.t,
            command=lambda value: self._actualizar_label(value, lbl_t_valor)
        )
        scale_t.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # --- Sigma (solo si no es isotrópico) ---
        if not self.isotropico:
            ttk.Label(label_parametros, text="Desviación Estándar (σ):").grid(row=1, column=0, sticky="w", pady=(10, 3))
            lbl_sigma_valor = ttk.Label(label_parametros, text=f"{self.sigma.get():.0f}", width=4)
            lbl_sigma_valor.grid(row=1, column=2, sticky="e", padx=(10, 0))

            scale_sigma = ttk.Scale(
                label_parametros,
                from_=1,
                to=100,
                orient="horizontal",
                variable=self.sigma,
                command=lambda value: self._actualizar_label(value, lbl_sigma_valor)
            )
            scale_sigma.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    # --- Actualiza solo el label, sin aplicar la transformación ---
    def _actualizar_label(self, value, label):
        valor = round(float(value))
        label.config(text=str(valor))

    def _on_apply(self):
        t = int(self.t.get())
        sigma = int(self.sigma.get())
        self.app._aplicar_transformacion(
            self.copia_imagen,
            aplicar_filtro_difusion,
            sigma=sigma,
            t=t,
            isotropico=self.isotropico
        )
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
        self.umbral_pendiente = tk.IntVar(value=128)
        self.sigma = tk.DoubleVar(value=1.0)
        self.log = config['log']

        # --- Labelframe de opciones ---
        grupo_opciones = ttk.Labelframe(self.frame_herramienta, text="Opciones", padding=10)
        grupo_opciones.pack(fill="x", padx=10, pady=5, expand=True)
        grupo_opciones.columnconfigure(1, weight=1)

        if self.log:
            # Label sigma
            ttk.Label(grupo_opciones, text="Desviación Estándar (σ):").grid(row=0, column=0, sticky="w", pady=(5, 0))
            lbl_sigma_valor = ttk.Label(grupo_opciones, text=f"{self.sigma.get():.0f}", width=4)
            lbl_sigma_valor.grid(row=0, column=2, sticky="e", padx=(10,0))

            # Scale sigma
            scale_sigma = ttk.Scale(
                grupo_opciones,
                from_=1,
                to=100,
                orient="horizontal",
                variable=self.sigma,
                command=lambda value: self._actualizar_sigma(value, lbl_sigma_valor)
            )
            scale_sigma.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

            # Label tamaño de máscara
            self.label_sigma = ttk.Label(
                grupo_opciones,
                text=f"Tamaño de máscara correspondiente (k): {int((int(self.sigma.get())*4)+1)}"
            )
            self.label_sigma.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # --- Checkbutton para usar pendiente ---
        check_pendiente = ttk.Checkbutton(
            grupo_opciones,
            text="Usar Evaluación de la Pendiente (con umbral)",
            variable=self.usar_pendiente,
            command=self._toggle_umbral_slider
        )
        check_pendiente.grid(row=2, column=0, columnspan=3, sticky="w", pady=5)

        # --- Frame del slider de umbral ---
        self.frame_umbral = ttk.Frame(grupo_opciones)
        ttk.Label(self.frame_umbral, text="Umbral:").grid(row=0, column=0, sticky="w", pady=(5, 0))
        self.lbl_umbral_valor = ttk.Label(self.frame_umbral, text=f"{self.umbral_pendiente.get():.0f}", width=4)
        self.lbl_umbral_valor.grid(row=0, column=2, sticky="e", padx=(10,0))
        scale_umbral = ttk.Scale(
            self.frame_umbral,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.umbral_pendiente,
            command=lambda value: self.lbl_umbral_valor.config(text=str(round(float(value))))
        )
        scale_umbral.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.frame_umbral.columnconfigure(1, weight=1)

        self._toggle_umbral_slider()
        self._finalizar_y_posicionar()

    def _actualizar_sigma(self, value, label):
        """Actualiza label y tamaño de máscara k."""
        valor = round(float(value))
        label.config(text=str(valor))
        k = 4 * valor + 1
        self.label_sigma.config(text=f"Tamaño de máscara correspondiente (k): {k}")

    def _toggle_umbral_slider(self):
        """Muestra u oculta el slider del umbral según el estado del checkbox."""
        if self.usar_pendiente.get():
            self.frame_umbral.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        else:
            self.frame_umbral.grid_forget()

    def _on_apply(self):
        pendiente = self.usar_pendiente.get()
        umbral = int(self.umbral_pendiente.get())
        sigma = int(self.sigma.get())
        log = self.log
        
        self.app._aplicar_transformacion(
            self.copia_imagen,
            aplicar_metodo_del_laplaciano,
            log=log,
            pendiente=pendiente,
            umbral=umbral,
            sigma=sigma
        )
        self.destroy()

class DialogoBilateral(DialogoHerramienta):
    """
    Diálogo para aplicar el filtro Bilateral.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Filtro Bilateral")
        
        self.copia_imagen = self.app.imagen_procesada.copy()

        self.sigma_s = tk.DoubleVar(value=1.0)
        self.sigma_r = tk.DoubleVar(value=1.0)

        # --- Labelframe principal ---
        grupo_opciones = ttk.Labelframe(self.frame_herramienta, text="Parámetros", padding=10)
        grupo_opciones.pack(fill="x", padx=10, pady=5, expand=True)
        grupo_opciones.columnconfigure(1, weight=1)

        # --- Sigma_s ---
        ttk.Label(grupo_opciones, text="Constante de suavizado espacial (σ_s):").grid(row=0, column=0, sticky="w", pady=(5, 0))
        lbl_sigma_s_valor = ttk.Label(grupo_opciones, text=f"{self.sigma_s.get():.0f}", width=4)
        lbl_sigma_s_valor.grid(row=0, column=2, sticky="e", padx=(10, 0))

        scale_sigma_s = ttk.Scale(
            grupo_opciones,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.sigma_s,
            command=lambda value: self._actualizar_label(value, lbl_sigma_s_valor, actualizar_k=True)
        )
        scale_sigma_s.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # --- Sigma_r ---
        ttk.Label(grupo_opciones, text="Constante de suavizado de intensidad (σ_r):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        lbl_sigma_r_valor = ttk.Label(grupo_opciones, text=f"{self.sigma_r.get():.0f}", width=4)
        lbl_sigma_r_valor.grid(row=1, column=2, sticky="e", padx=(10, 0))

        scale_sigma_r = ttk.Scale(
            grupo_opciones,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.sigma_r,
            command=lambda value: self._actualizar_label(value, lbl_sigma_r_valor)
        )
        scale_sigma_r.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # --- Tamaño de máscara ---
        grupo_tamano = ttk.Labelframe(self.frame_herramienta, text="Tamaño", padding=10)
        grupo_tamano.pack(fill="x", padx=10, pady=5, expand=True)

        self.label_sigma = ttk.Label(
            grupo_tamano,
            text=f"Tamaño de máscara correspondiente (k): {int((int(self.sigma_s.get())*2)+1)}"
        )
        self.label_sigma.pack(padx=5, pady=(0, 10))

        self._finalizar_y_posicionar()

    def _actualizar_label(self, value, label, actualizar_k=False):
        """Actualiza solo el label del slider; si actualizar_k=True, actualiza tamaño de máscara."""
        valor = round(float(value))
        label.config(text=str(valor))
        if actualizar_k:
            k = 2 * valor + 1
            self.label_sigma.config(text=f"Tamaño de máscara correspondiente (k): {k}")

    def _on_apply(self):
        sigma_s = int(self.sigma_s.get())
        sigma_r = int(self.sigma_r.get())
        self.app._aplicar_transformacion(
            self.copia_imagen,
            aplicar_filtro_bilateral,
            sigma_s=sigma_s,
            sigma_r=sigma_r
        )
        self.destroy()

class DialogoCanny(DialogoHerramienta):
    """
    Diálogo para aplicar detector de Canny a una imagen.
    """
    def __init__(self, parent, app_principal):
        super().__init__(parent, app_principal, "Detector de Canny")
        
        self.copia_imagen = self.app.imagen_procesada.copy()

        self.t1 = tk.IntVar(value=50)
        self.t2 = tk.IntVar(value=150)

        # --- Labelframe principal ---
        label_parametros = ttk.Labelframe(self.frame_herramienta, text="Parámetros", padding=10)
        label_parametros.pack(fill="x", padx=10, pady=5, expand=True)
        label_parametros.columnconfigure(1, weight=1)

        ttk.Label(label_parametros, text="Umbral t1:").grid(row=0, column=0, sticky="w", pady=(0, 3))
        label_t1 = ttk.Label(label_parametros, text=f"{self.t1.get():.0f}", width=4)
        label_t1.grid(row=0, column=2, sticky="e", padx=(10, 0))

        scale_t1 = ttk.Scale(
            label_parametros,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.t1,
            length=250,
            command=lambda value: self._actualizar_label(value, label_t1)
        )
        scale_t1.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(label_parametros, text="Umbral t2:").grid(row=1, column=0, sticky="w", pady=(0, 3))
        label_t2 = ttk.Label(label_parametros, text=f"{self.t2.get():.0f}", width=4)
        label_t2.grid(row=1, column=2, sticky="e", padx=(10, 0))

        scale_t2 = ttk.Scale(
            label_parametros,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.t2,
            length=250,
            command=lambda value: self._actualizar_label(value, label_t2)
        )
        scale_t2.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self._finalizar_y_posicionar(self.app.canvas_izquierdo)

    # --- Actualiza solo el label, sin aplicar la transformación ---
    def _actualizar_label(self, value, label):
        valor = round(float(value))
        label.config(text=str(valor))

    def _on_apply(self):
        t1 = int(self.t1.get())
        t2 = int(self.t2.get())
        self.app._aplicar_transformacion(
            self.copia_imagen,
            aplicar_detector_canny,
            t1=t1,
            t2=t2,
            byn=True
        )
        self.destroy()
    
    def _on_cancel(self):
        self.app._cancelar_cambio(self.copia_imagen)
        self.destroy() 