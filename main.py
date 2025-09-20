# Librerias
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageChops
import numpy as np
from typing import Optional, Tuple, Callable
import matplotlib.pyplot as plt
import webbrowser

# Importaciones de código en archivos
from utils import requiere_imagen, refrescar_imagen
from ui_dialogs import (DialogoBase, DialogoDimensiones, DialogoResultado, DialogoHerramienta, DialogoGamma, DialogoUmbralizacion,
                        DialogoHistogramas, DialogoHistogramaDist,
                        DialogoRuido,
                        DialogoFiltro, DialogoFiltroMedia, DialogoFiltroMediana, DialogoFiltroMedianaPonderada, DialogoFiltroGaussiano, DialogoFiltroRealce
                        )
from processing import escalar_255, aplicar_negativo

def abrir_github(event):
    webbrowser.open_new("https://github.com/matias-cisnero/procesamiento_imagenes")

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---

class EditorDeImagenes:
    GEOMETRIA_VENTANA = "1200x800+200+15"
    FORMATOS_IMAGEN = [("Imágenes Soportadas", "*.jpg *.jpeg *.png *.bmp *.pgm *.raw"), ("Todos los archivos", "*.*")]
    CANALES_RGB = ("R", "G", "B")
    ZOOM_MIN, ZOOM_MAX = 0.1, 3.0

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Procesador de Imágenes")
        self.root.geometry(self.GEOMETRIA_VENTANA)
        self.root.iconbitmap("favicon.ico")

        self.imagen_original: Optional[Image.Image] = None
        self.imagen_procesada: Optional[Image.Image] = None
        self.pixel_seleccionado: Optional[Tuple[int, int]] = None
        self.on_region_select_callback: Optional[Callable] = None
        self.zoom_level = 1.0

        self.rgb_vars = {c: tk.StringVar(value="") for c in self.CANALES_RGB}
        self.zoom_var = tk.StringVar(value="100.0%")
        self.analisis_vars = {"total": tk.StringVar(value="-"), "r": tk.StringVar(value="-"), "g": tk.StringVar(value="-"), "b": tk.StringVar(value="-"), "gris": tk.StringVar(value="-")}
        
        # Carga de iconos
        self.icono_cargar = tk.PhotoImage(file="icons/cargar.png").subsample(5,5)
        self.icono_guardar = tk.PhotoImage(file="icons/guardar.png").subsample(5,5)
        self.icono_salir = tk.PhotoImage(file="icons/salir.png").subsample(5,5)

        self.icono_imagen_original = tk.PhotoImage(file="icons/imagen_original.png").subsample(5,5)
        self.icono_escala_grises = tk.PhotoImage(file="icons/escala_grises.png").subsample(5,5)
        self.icono_pixel = tk.PhotoImage(file="icons/pixel.png").subsample(5,5)
        self.icono_recorte = tk.PhotoImage(file="icons/recorte.png").subsample(5,5)
        self.icono_analisis = tk.PhotoImage(file="icons/analisis.png").subsample(5,5)
        self.icono_resta_imagenes = tk.PhotoImage(file="icons/resta_imagenes.png").subsample(5,5)
        self.icono_github = tk.PhotoImage(file="icons/github.png").subsample(5,5)

        self.icono_gamma = tk.PhotoImage(file="icons/gamma.png").subsample(5,5)
        self.icono_umbralizacion = tk.PhotoImage(file="icons/umbralizacion.png").subsample(5,5)
        self.icono_negativo = tk.PhotoImage(file="icons/negativo2.png").subsample(5,5)

        self.icono_histograma = tk.PhotoImage(file="icons/histograma.png").subsample(5,5)
        self.icono_ecualizacion = tk.PhotoImage(file="icons/ecualizacion.png").subsample(5,5)
        self.icono_normal = tk.PhotoImage(file="icons/normal.png").subsample(5,5)
        self.icono_rayleigh = tk.PhotoImage(file="icons/rayleigh.png").subsample(5,5)
        self.icono_exponencial = tk.PhotoImage(file="icons/exponencial.png").subsample(5,5)
        self.icono_sal_y_pimienta = tk.PhotoImage(file="icons/sal_y_pimienta.png").subsample(5,5)

        self.icono_media = tk.PhotoImage(file="icons/media.png").subsample(5,5)
        self.icono_mediana = tk.PhotoImage(file="icons/mediana.png").subsample(5,5)
        self.icono_mediana_ponderada = tk.PhotoImage(file="icons/mediana_ponderada.png").subsample(5,5)
        self.icono_borde = tk.PhotoImage(file="icons/borde.png").subsample(5,5)

        # Atajos de teclado
        self.root.bind("<Control-s>", self._guardar_imagen_como)
        self.root.bind("<Control-z>", self._volver_imagen_original)

        self._setup_ui()
        self._vincular_eventos()

    # --- 1. CONFIGURACIÓN DE LA UI PRINCIPAL ---
    def _setup_ui(self):
        self._crear_menu()
        panel_principal = tk.Frame(self.root)
        panel_principal.pack(fill=tk.BOTH, expand=True)
        panel_principal.grid_columnconfigure(0, weight=1)
        panel_principal.grid_columnconfigure(1, weight=1)
        panel_principal.grid_columnconfigure(2, minsize=250)
        panel_principal.grid_rowconfigure(0, weight=1)

        self._crear_visores_de_imagen(panel_principal)
        self._crear_panel_control_fijo(panel_principal)
        self._crear_controles_zoom()

    def _crear_menu(self):
        barra_menu = tk.Menu(self.root)
        self.root.config(menu=barra_menu)
        
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cargar Imagen...", image=self.icono_cargar, compound="left", command=self._cargar_imagen)
        menu_archivo.add_command(label="Guardar Imagen Como...", image=self.icono_guardar, compound="left", command=self._guardar_imagen_como, accelerator="Ctrl+S")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", image=self.icono_salir, compound="left", command=self.root.quit)
        
        menu_operadores_puntuales = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Operadores Puntuales", menu=menu_operadores_puntuales)
        menu_operadores_puntuales.add_command(label="Transformación Gamma", image=self.icono_gamma, compound="left", command=lambda: self._iniciar_dialogo(DialogoGamma))
        menu_operadores_puntuales.add_command(label="Umbralización", image=self.icono_umbralizacion, compound="left", command=lambda: self._iniciar_dialogo(DialogoUmbralizacion))
        menu_operadores_puntuales.add_command(label="Negativo", image=self.icono_negativo, compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_negativo))

        menu_histogramas = tk.Menu(barra_menu, tearoff=0)
        config_dist_gaussiano = {'titulo': "Histograma Gaussiano", 'param_label': "Desviación Estándar (σ):", 'distribucion': np.random.normal}
        config_dist_rayleigh = {'titulo': "Histograma Rayleigh", 'param_label': "Parámetro Xi (ξ):", 'distribucion': np.random.rayleigh}
        config_dist_exponencial = {'titulo': "Histograma Exponencial", 'param_label': "Lambda (λ):", 'distribucion': np.random.exponential}
        barra_menu.add_cascade(label="Histogramas", menu=menu_histogramas)
        menu_histogramas.add_command(label="Niveles de Gris y RGB", image=self.icono_histograma, compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramas))
        menu_histogramas.add_command(label="Ecualización", image=self.icono_ecualizacion, compound="left", command=self._aplicar_ecualizacion_histograma)
        menu_histogramas.add_command(label="Generador Gaussiano", image=self.icono_normal, compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_gaussiano))
        menu_histogramas.add_command(label="Generador Rayleigh", image=self.icono_rayleigh, compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_rayleigh))
        menu_histogramas.add_command(label="Generador Exponencial", image=self.icono_exponencial, compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_exponencial))

        menu_ruido = tk.Menu(barra_menu, tearoff=0)
        config_gaussiano = {'titulo': "Ruido Gaussiano", 'param_label': "Desviación Estándar (σ):", 'distribucion': np.random.normal, 'sal_y_pimienta': False, 'res': 1}
        config_rayleigh = {'titulo': "Ruido Rayleigh", 'param_label': "Parámetro Xi (ξ):", 'distribucion': np.random.rayleigh, 'sal_y_pimienta': False, 'res': 1}
        config_exponencial = {'titulo': "Ruido Exponencial", 'param_label': "Lambda (λ):", 'distribucion': np.random.exponential, 'sal_y_pimienta': False, 'res': 1}
        config_sal_y_pimienta = {'titulo': "Sal y Pimienta", 'param_label': "-", 'distribucion': np.random.normal, 'sal_y_pimienta': True, 'res': 2}
        barra_menu.add_cascade(label="Ruido", menu=menu_ruido)
        menu_ruido.add_command(label="Gaussiano", image=self.icono_normal, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_gaussiano))
        menu_ruido.add_command(label="Rayleigh", image=self.icono_rayleigh, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_rayleigh))
        menu_ruido.add_command(label="Exponencial", image=self.icono_exponencial, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_exponencial))
        menu_ruido.add_command(label="Sal y Pimienta", image=self.icono_sal_y_pimienta, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_sal_y_pimienta))
        #menu_ruido.add_command(label="Sal y Pimienta", image=self.icono_sal_y_pimienta, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuidoSalYPimienta))

        menu_filtros = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Filtros", menu=menu_filtros)
        menu_filtros.add_command(label="Media", image=self.icono_media, compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltroMedia))
        menu_filtros.add_command(label="Mediana", image=self.icono_mediana, compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltroMediana))
        menu_filtros.add_command(label="Mediana Ponderada", image=self.icono_mediana_ponderada, compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltroMedianaPonderada))
        menu_filtros.add_command(label="Gaussiano", image=self.icono_normal, compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltroGaussiano))
        menu_filtros.add_command(label="Realce de Bordes", image=self.icono_borde, compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltroRealce))
        menu_filtros.add_command(label="Prewitt Horizontal", image=self.icono_borde, compound="left", command=lambda: self._aplicar_filtro_directo(self._filtro_prewitt_h))
        menu_filtros.add_command(label="Prewitt Vertical", image=self.icono_borde, compound="left", command=lambda: self._aplicar_filtro_directo(self._filtro_prewitt_v))
        menu_filtros.add_command(label="Sobel Horizontal", image=self.icono_borde, compound="left", command=lambda: self._aplicar_filtro_directo(self._filtro_sobel_h))
        menu_filtros.add_command(label="Sobel Vertical", image=self.icono_borde, compound="left", command=lambda: self._aplicar_filtro_directo(self._filtro_sobel_v))
        menu_filtros.add_command(label="Filtro Prueba", image=self.icono_borde, compound="left", command=self._aplicar_filtro_prueba)


    def _crear_visores_de_imagen(self, parent: tk.Frame):
        frame_visores = tk.Frame(parent)
        frame_visores.grid(row=0, column=0, columnspan=2, sticky="nsew")
        frame_visores.grid_rowconfigure(0, weight=1)
        frame_visores.grid_columnconfigure(0, weight=1)
        frame_visores.grid_columnconfigure(1, weight=1)
        self.canvas_izquierdo = self._crear_panel_canvas(frame_visores, 0, "Imagen Original")
        self.canvas_derecho = self._crear_panel_canvas(frame_visores, 1, "Imagen Modificada")

        scroll_y = ttk.Scrollbar(frame_visores, orient=tk.VERTICAL, command=self._scroll_y_view)
        scroll_x = ttk.Scrollbar(frame_visores, orient=tk.HORIZONTAL, command=self._scroll_x_view)
        self.canvas_izquierdo.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.canvas_derecho.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.grid(row=0, column=2, sticky="ns")
        scroll_x.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _scroll_y_view(self, *args):
        self.canvas_izquierdo.yview(*args)
        self.canvas_derecho.yview(*args)

    def _scroll_x_view(self, *args):
        self.canvas_izquierdo.xview(*args)
        self.canvas_derecho.xview(*args)

    def _crear_panel_canvas(self, parent: tk.Frame, col: int, titulo: str) -> tk.Canvas:
        frame = ttk.Labelframe(parent, text=titulo, padding=5)
        frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        canvas = tk.Canvas(frame, bg="gray")
        canvas.pack(fill=tk.BOTH, expand=True)
        return canvas

    def _crear_panel_control_fijo(self, parent: tk.Frame):
        panel_control = ttk.Frame(parent, padding=10)
        panel_control.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)

        frame_imagen_original = ttk.Labelframe(panel_control, text="Volver a imagen original", padding=10)
        frame_imagen_original.pack(fill=tk.X, pady=5)
        ttk.Button(frame_imagen_original, text="Volver", image=self.icono_imagen_original, compound="left", command=self._volver_imagen_original).pack(fill=tk.X)

        frame_escala_grises = ttk.Labelframe(panel_control, text="Convertir a escala de grises", padding=10)
        frame_escala_grises.pack(fill=tk.X, pady=5)
        ttk.Button(frame_escala_grises, text="Convertir", image=self.icono_escala_grises, compound="left", command=self._escala_grises).pack(fill=tk.X)
        
        frame_pixel = ttk.Labelframe(panel_control, text="Edición de Píxel", padding=10)
        frame_pixel.pack(fill=tk.X, pady=5)
        
        pixel_grid = ttk.Frame(frame_pixel)
        pixel_grid.pack(fill=tk.X)
        self.color_preview = tk.Canvas(pixel_grid, width=40, height=40, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.color_preview.grid(row=0, column=2, rowspan=3, padx=(10, 0))
        for i, canal in enumerate(self.CANALES_RGB):
            ttk.Label(pixel_grid, text=f"{canal}:").grid(row=i, column=0, sticky="w")
            ttk.Entry(pixel_grid, textvariable=self.rgb_vars[canal], width=5).grid(row=i, column=1, padx=5)
        
        ttk.Button(frame_pixel, text="Activar Selección de Píxel", image=self.icono_pixel, compound="left", command=self._activar_modo_seleccion).pack(fill=tk.X, pady=(10,0))
        
        frame_recorte = ttk.Labelframe(panel_control, text="Recortar Región", padding=10)
        frame_recorte.pack(fill=tk.X, pady=5)
        ttk.Button(frame_recorte, text="Activar Selección para Recorte", image=self.icono_recorte, compound="left", command=self._activar_modo_recorte).pack(fill=tk.X)

        frame_analisis = ttk.Labelframe(panel_control, text="Análisis de Región", padding=10)
        frame_analisis.pack(fill=tk.X, pady=5)
        
        def add_analisis_row(parent, label, var, row):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=1)
            ttk.Label(parent, textvariable=var).grid(row=row, column=1, sticky="w", padx=5)

        add_analisis_row(frame_analisis, "Total Píxeles:", self.analisis_vars["total"], 0)
        ttk.Separator(frame_analisis, orient=tk.HORIZONTAL).grid(row=1, columnspan=2, sticky="ew", pady=5)
        add_analisis_row(frame_analisis, "Promedio R:", self.analisis_vars["r"], 2)
        add_analisis_row(frame_analisis, "Promedio G:", self.analisis_vars["g"], 3)
        add_analisis_row(frame_analisis, "Promedio B:", self.analisis_vars["b"], 4)
        add_analisis_row(frame_analisis, "Promedio Gris:", self.analisis_vars["gris"], 5)
        
        ttk.Button(frame_analisis, text="Activar Análisis de Región", image=self.icono_analisis, compound="left", command=self._activar_modo_analisis).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10,0))

        frame_resta_imagenes = ttk.Labelframe(panel_control, text="Resta de Imagenes", padding=10)
        frame_resta_imagenes.pack(fill=tk.X, pady=5)

        ttk.Button(frame_resta_imagenes, text="Restar Imagenes", image=self.icono_resta_imagenes, compound="left", command=self._iniciar_resta).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))

        label_github = ttk.Label(panel_control, text="Mi repositorio en GitHub", foreground="blue", cursor="hand2", image=self.icono_github, compound="left")
        label_github.pack(fill=tk.X, pady=5)
        label_github.bind("<Button-1>", abrir_github)
        
    def _crear_controles_zoom(self):
        zoom_frame = ttk.Labelframe(self.root, text="Zoom", padding=5)
        zoom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        ttk.Label(zoom_frame, text=f"{self.ZOOM_MIN*100:.0f}%").pack(side=tk.LEFT, padx=(5,0))
        self.zoom_slider = ttk.Scale(zoom_frame, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, command=self._actualizar_zoom_desde_slider)
        self.zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(zoom_frame, text=f"{self.ZOOM_MAX*100:.0f}%").pack(side=tk.LEFT, padx=(0,5))
        
        self.zoom_spinbox = ttk.Spinbox(
            zoom_frame, 
            from_=self.ZOOM_MIN*100, 
            to=self.ZOOM_MAX*100, 
            textvariable=self.zoom_var, 
            width=8, 
            command=self._actualizar_zoom_desde_spinbox
        )
        self.zoom_spinbox.pack(side=tk.RIGHT, padx=5)
        self.zoom_spinbox.bind("<Return>", self._actualizar_zoom_desde_spinbox)

    # =======================================================================================
    #                              2. LÓGICA DE HERRAMIENTAS
    # =======================================================================================
        
    # --- Iniciar Dialogo

    @requiere_imagen
    def _iniciar_dialogo(self, dialogo_clase, **kwargs):
        """
        Método genérico para abrir cualquier diálogo de herramienta que necesite
        una referencia a la app principal.
        """
        #print("Sí, jeje, funciona")
        dialogo = dialogo_clase(self.root, self, **kwargs)

    # --- Cancelar Cambio

    @refrescar_imagen
    def _cancelar_cambio(self, imagen):
        self.imagen_procesada = imagen

    # ===============================((OPERADORES_PUNTUALES))================================

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_transformacion(self, imagen, funcion, *args, **kwargs):
        print("Funciona bien!!")
        imagen_np = np.array(imagen.convert('RGB')) 

        resultado_np = funcion(imagen_np, *args, **kwargs)

        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8'))

    # ================================((HISTOGRAMAS))========================================

    # --- Niveles de Gris y RGB

    def _tomar_niveles_grisrgb_aplanados(self):
        """
        Prepara y devuelve un diccionario con los datos aplanados para los 4 histogramas.
        """
        imagen_np = np.array(self.imagen_procesada)
        
        # Datos para el histograma de grises
        imagen_gris_pil = self.imagen_procesada.convert('L')
        datos_gris = np.array(imagen_gris_pil).flatten()
        
        # Datos para los canales RGB
        datos_r = imagen_np[:, :, 0].flatten()
        datos_g = imagen_np[:, :, 1].flatten()
        datos_b = imagen_np[:, :, 2].flatten()
        
        # Devolvemos todo en un diccionario
        return {
            'gris': datos_gris,
            'rojo': datos_r,
            'verde': datos_g,
            'azul': datos_b
        }

    # --- Ecualización

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_ecualizacion_histograma(self):
        """
        Realiza la ecualización del histograma.
        """
        # Array de la forma (m. n).
        imagen_np_gris = np.array(self.imagen_procesada.convert('L'))
        datos_gris = imagen_np_gris.flatten()

        n_r = np.bincount(datos_gris, minlength=256) # Freq abs(ni)
        NM = datos_gris.size # Pixels totales(n)
        h_r = n_r / NM # Freq relativa(ni/n)

        # Hacemos la suma acumulada
        sk = np.zeros(256)
        for k in range(len(sk)):
            sk[k] = np.sum(h_r[0:k+1])
        
        sk_sombrero = escalar_255(sk) # Discretizamos
        resultado_np = sk_sombrero[imagen_np_gris] # Lookup table

        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8')).convert('RGB')

    # ===================================((RUIDO))===========================================

    # -- Aditivo y Multiplicativo

    @refrescar_imagen
    def _aplicar_ruido(self, imagen, tipo, vector_ruido, d):
        """
        Aplica un vector de ruido a una imagen de forma aditiva o multiplicativa.
        """
        # Transformar la imágen en un formato adecuado
        imagen_np = np.array(imagen).astype(float)
        m, n, _ = imagen_np.shape # Esto es para quedarme con 256 x 256 e ignorar los 3 canales rgb

        # Cantidad de píxeles contaminados
        num_contaminados = int((d * (m * n)) / 100)
        # num_contaminados = len(vector_ruido)
        D = np.unravel_index(np.random.choice(m * n, num_contaminados, replace=False),(m, n))

        # Generar la imagen contaminada I_c
        if tipo == "Aditivo": imagen_np[D] += vector_ruido
        elif tipo == "Multiplicativo": imagen_np[D] *= vector_ruido
        
        resultado_np = escalar_255(imagen_np)
        self.imagen_procesada = Image.fromarray(resultado_np)

    # --- Generar Vector Ruido (Gaussiano, Rayleigh, Exponencial)

    def _generar_vector_ruido(self, distribucion, intensidad, cantidad):
        # distribucion = np.random.normal, np.random.rayleigh, np.random.exponential
        vector_aleatorio = distribucion(scale=intensidad, size=(cantidad, 1))

        return vector_aleatorio

    # --- Sal y Pimienta

    @refrescar_imagen
    def _aplicar_ruido_sal_y_pimienta(self, imagen, p):
        imagen_np = np.array(imagen.convert('RGB'))

        m, n, _ = imagen_np.shape

        for i in range(m):
            for j in range(n):
                x = np.random.rand()
                if x <= p:
                    imagen_np[i, j, :] = 0 # pimienta (negro)
                elif x > (1-p):
                    imagen_np[i, j, :] = 255 # sal (blanco)

        self.imagen_procesada = Image.fromarray(imagen_np)

    # ===================================((FILTROS))=========================================

    # --- Filtrado en el Dominio Espacial

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_filtro(self, imagen, filtro, factor):
        """
        Aplica un filtro a la imagen.
        """
        imagen_np = np.array(imagen.convert('RGB')).astype(float)

        m, n, _ = imagen_np.shape
        k, l = filtro.shape
        pad_h, pad_w = k//2, l//2

        # Padding e imagen filtrada
        imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
        imagen_filtrada = np.zeros_like(imagen_np)

        # Bucle para filtrado (c para los canales)
        for i in range(m):
            for j in range(n):
                for c in range(3):
                    region = imagen_padded[i:i+k, j:j+l, c]
                    
                    valor = np.sum(region * filtro) * factor
                    
                    imagen_filtrada[i, j, c] = valor

        #resultado_np = np.clip(imagen_filtrada, 0, 255).astype(np.uint8)
        resultado_np = escalar_255(imagen_filtrada)

        self.imagen_procesada = Image.fromarray(resultado_np)

    # --- Media

    def _filtro_media(self, k):
        filtro = np.ones((k, k))

        factor = 1 / np.sum(filtro)
        return (filtro, factor)

    # --- Mediana

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_filtro_mediana(self, imagen, filtro):
        imagen_np = np.array(imagen.convert('RGB')).astype(float)

        m, n, _ = imagen_np.shape
        k, l = filtro.shape
        pad_h, pad_w = k//2, l//2

        # Padding e imagen filtrada
        imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
        imagen_filtrada = np.zeros_like(imagen_np)

        indices_repeticion = filtro.flatten().astype(int)

        # Bucle para filtrado (c para los canales)
        for i in range(m):
            for j in range(n):
                for c in range(3):
                    region = imagen_padded[i:i+k, j:j+l, c]
                    valores = np.repeat(region.flatten(), indices_repeticion) # Indica cuantas veces se repite cada indice
                    mediana = np.median(valores)
                    imagen_filtrada[i, j, c] = mediana
        self.imagen_procesada = Image.fromarray(imagen_filtrada.astype(np.uint8))

    # --- Mediana Ponderada

    def _filtro_mediana_ponderada(self, k):
        filtro_gauss, _ = self._filtro_gaussiano(k)
        filtro = (filtro_gauss * 50).astype(int)

        factor = 1
        return (filtro, factor)

    # --- Gaussiano

    def _filtro_gaussiano(self, k):
        filtro = np.ones((k, k)).astype(float)
        u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
        sigma = (k-1) / 2

        for x in range(k):
            for y in range(k):
                filtro[x, y] = (1 / (2 * np.pi * sigma**2)) * np.exp(-((x - u)**2 + (y - u)**2)/(sigma**2))

        factor = 1 / np.sum(filtro)
        #print(f"Factor usado: {1} / {np.sum(filtro)}")
        return (filtro, factor)

    # --- Realce de Bordes

    def _filtro_realce(self, k):
        filtro = -1 * np.ones((k, k))
        filtro[k//2, k//2] = k**2 - 1

        factor = 1
        return (filtro, factor)
    
    def _aplicar_filtro_directo(self, funcion):
        filtro, factor = funcion(k=3)
        self._aplicar_filtro(self.imagen_procesada, filtro, factor)

    def _filtro_prewitt_h(self, k):
        filtro = np.array([[-1, -1, -1],
                           [0, 0, 0],
                           [1, 1, 1]])
        factor = 1 # usar 1 / 9
        return (filtro, factor)
    
    def _filtro_prewitt_v(self, k):
        filtro = np.array([[-1, 0, 1],
                           [-1, 0, 1],
                           [-1, 0, 1]])
        factor = 1 # usar 1 / 9
        return (filtro, factor)
    
    def _filtro_sobel_h(self, k):
        filtro = np.array([[-1, -2, -1],
                           [0, 0, 0],
                           [1, 2, 1]])
        factor = 1
        return (filtro, factor)
    
    def _filtro_sobel_v(self, k):
        filtro = np.array([[-1, 0, 1],
                           [-2, 0, 2],
                           [-1, 0, 1]])
        factor = 1
        return (filtro, factor)
    
    def _obtener_imagen_filtrada(self, imagen, filtro, factor):
        imagen_np = np.array(imagen.convert('RGB')).astype(float)

        m, n, _ = imagen_np.shape
        k, l = filtro.shape
        pad_h, pad_w = k//2, l//2

        # Padding e imagen filtrada
        imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
        imagen_filtrada = np.zeros_like(imagen_np)

        # Bucle para filtrado (c para los canales)
        for i in range(m):
            for j in range(n):
                for c in range(3):
                    region = imagen_padded[i:i+k, j:j+l, c]
                    
                    valor = np.sum(region * filtro) * factor
                    
                    imagen_filtrada[i, j, c] = valor

        #resultado_np = np.clip(imagen_filtrada, 0, 255).astype(np.uint8)
        #resultado_np = escalar_255(imagen_filtrada)

        return imagen_filtrada

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_filtro_prueba(self):
        k=3
        filtro1, factor1 = self._filtro_prewitt_v(k)
        filtro2, factor2 = self._filtro_prewitt_h(k)

        img1 = self._obtener_imagen_filtrada(self.imagen_procesada, filtro1, factor1)
        img2 = self._obtener_imagen_filtrada(self.imagen_procesada, filtro2, factor2)

        imagen_filtrada = np.sqrt((img1**2)+(img2**2))

        resultado_np = escalar_255(imagen_filtrada)

        self.imagen_procesada = Image.fromarray(resultado_np)

    


    # ===========================((HERRAMIENTAS_GENERALES))==================================

    @requiere_imagen
    @refrescar_imagen
    def _volver_imagen_original(self, event=None):
        self.imagen_procesada = self.imagen_original

    @requiere_imagen
    @refrescar_imagen
    def _escala_grises(self):
        self.imagen_procesada = self.imagen_procesada.convert('L').convert('RGB')
    
    @requiere_imagen
    def _iniciar_resta(self):
        ruta_img2 = filedialog.askopenfilename(title="Seleccionar imagen a restar", filetypes=self.FORMATOS_IMAGEN)
        if not ruta_img2: return

        try:
            img2 = Image.open(ruta_img2).convert("RGB")
            if self.imagen_procesada.size != img2.size:
                messagebox.showerror("Error de Dimensiones", "Las imágenes deben tener el mismo tamaño.")
                return
            
            resultado = ImageChops.subtract(image1=self.imagen_procesada, image2=img2, scale=1.0, offset=0) # mirar
            self._mostrar_ventana_resultado(resultado, "Resultado de la Resta")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar o procesar la imagen.\n{e}")

    @requiere_imagen
    def _activar_modo_seleccion(self):
        self._desactivar_modos()
        self.pixel_seleccionado = None
        self.canvas_derecho.config(cursor="crosshair")
        self.canvas_derecho.bind("<Button-1>", self._fijar_pixel_seleccionado)
        self.canvas_derecho.bind("<Motion>", self._mostrar_info_pixel_hover)

    @requiere_imagen
    def _activar_modo_recorte(self):
        self._desactivar_modos()
        self._activar_modo_region(self._on_release_recorte)

    @requiere_imagen
    def _activar_modo_analisis(self):
        self._desactivar_modos()
        self._limpiar_resultados_analisis()
        self._activar_modo_region(self._on_release_analisis)

    # --- Lógica de Carga y Guardado ---
    def _cargar_imagen(self):
        ruta = filedialog.askopenfilename(title="Seleccionar Imagen", filetypes=self.FORMATOS_IMAGEN)
        if not ruta: return
        try:
            if ruta.lower().endswith(".raw"):
                dialogo = DialogoDimensiones(self.root)
                if not dialogo.resultado: return
                img = self._leer_raw_como_pil(ruta, *dialogo.resultado)
            else:
                img = Image.open(ruta)
            
            if img: self._finalizar_carga_imagen(img)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen.\n{e}")

    def _leer_raw_como_pil(self, ruta: str, ancho: int, alto: int) -> Optional[Image.Image]:
        try:
            total_pixeles = ancho * alto
            datos_raw = np.fromfile(ruta, dtype=np.uint8, count=total_pixeles)
            if datos_raw.size < total_pixeles:
                messagebox.showwarning("Error de Tamaño", f"El archivo es más pequeño de lo esperado para las dimensiones {ancho}x{alto}.", parent=self.root)
                datos_raw.resize(total_pixeles, refcheck=False)
            imagen_array = datos_raw.reshape((alto, ancho))
            return Image.fromarray(imagen_array, mode='L')
        except Exception as e:
            messagebox.showerror("Error al Leer RAW", f"No se pudo procesar el archivo RAW.\nError: {e}", parent=self.root)

    @refrescar_imagen
    def _finalizar_carga_imagen(self, imagen_pil: Image.Image):
        self.imagen_original = imagen_pil.convert("RGB")
        self.imagen_procesada = self.imagen_original.copy()
        self._ajustar_zoom_inicial()

    @requiere_imagen
    def _guardar_imagen_como(self, event=None):
        self._guardar_imagen_pil(self.imagen_procesada, "Guardar imagen como...")

    # --- Métodos de Soporte y Eventos ---
    def _vincular_eventos(self):
        for var in self.rgb_vars.values():
            var.trace_add("write", self._aplicar_cambio_color_en_vivo)

    def _actualizar_display_imagenes(self):
        if not self.imagen_original: return
        w, h = self.imagen_original.size
        w_zoom, h_zoom = int(w * self.zoom_level), int(h * self.zoom_level)
        for canvas, pil_image in [(self.canvas_izquierdo, self.imagen_original), (self.canvas_derecho, self.imagen_procesada)]:
            if pil_image:
                img_resized = pil_image.resize((w_zoom, h_zoom), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img_resized)
                canvas.delete("all")
                canvas.create_image(0, 0, anchor="nw", image=img_tk)
                canvas.image_ref = img_tk
                canvas.config(scrollregion=(0, 0, w_zoom, h_zoom))

    def _ajustar_zoom_inicial(self):
        self.root.update_idletasks()
        canvas_w = self.canvas_izquierdo.winfo_width()
        if self.imagen_original:
            img_w, _ = self.imagen_original.size
            if canvas_w > 1 and img_w > 0:
                ratio = min(1.0, canvas_w / img_w)
                self.zoom_var.set(f"{ratio * 100:.1f}%")
                self._actualizar_zoom_desde_spinbox()

    def _actualizar_zoom_desde_slider(self, valor_str: str):
        self.zoom_level = float(valor_str)
        self.zoom_var.set(f"{self.zoom_level * 100:.1f}%")
        self._actualizar_display_imagenes()
        
    def _actualizar_zoom_desde_spinbox(self, event=None):
        try:
            valor_str = self.zoom_var.get().replace('%', '')
            nuevo_nivel = float(valor_str) / 100.0
            nivel_limitado = max(self.ZOOM_MIN, min(self.ZOOM_MAX, nuevo_nivel))
            
            if nivel_limitado != nuevo_nivel:
                nuevo_nivel = nivel_limitado
                self.zoom_var.set(f"{nuevo_nivel * 100:.1f}%")
            
            self.zoom_level = nuevo_nivel
            self.zoom_slider.set(nuevo_nivel)
            self._actualizar_display_imagenes()
        except (ValueError, TypeError):
            self.zoom_var.set(f"{self.zoom_level * 100:.1f}%")

    @refrescar_imagen
    def _aplicar_cambio_color_en_vivo(self, *args):
        if not self.pixel_seleccionado: return False
        try:
            r, g, b = (int(self.rgb_vars[c].get()) for c in self.CANALES_RGB)
            if not all(0 <= val <= 255 for val in (r, g, b)): return False
            self.imagen_procesada.putpixel(self.pixel_seleccionado, (r, g, b))
            self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
        except ValueError:
            return False

    @requiere_imagen
    def _mostrar_info_pixel_hover(self, event):
        img_x = int(self.canvas_derecho.canvasx(event.x) / self.zoom_level)
        img_y = int(self.canvas_derecho.canvasy(event.y) / self.zoom_level)
        w, h = self.imagen_procesada.size
        if 0 <= img_x < w and 0 <= img_y < h:
            r, g, b = self.imagen_procesada.getpixel((img_x, img_y))
            self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
            if not self.pixel_seleccionado:
                self.rgb_vars["R"].set(str(r))
                self.rgb_vars["G"].set(str(g))
                self.rgb_vars["B"].set(str(b))

    def _desactivar_modos(self):
        self.canvas_derecho.config(cursor="")
        self.canvas_derecho.unbind("<Button-1>")
        self.canvas_derecho.unbind("<B1-Motion>")
        self.canvas_derecho.unbind("<ButtonRelease-1>")
        self.canvas_derecho.unbind("<Motion>")
        self.pixel_seleccionado = None

    @requiere_imagen
    def _fijar_pixel_seleccionado(self, event):
        img_x = int(self.canvas_derecho.canvasx(event.x) / self.zoom_level)
        img_y = int(self.canvas_derecho.canvasy(event.y) / self.zoom_level)
        w, h = self.imagen_procesada.size
        if 0 <= img_x < w and 0 <= img_y < h:
            self.pixel_seleccionado = (img_x, img_y)
            r, g, b = self.imagen_procesada.getpixel((img_x, img_y))
            self.rgb_vars["R"].set(str(r))
            self.rgb_vars["G"].set(str(g))
            self.rgb_vars["B"].set(str(b))
            
            self.canvas_derecho.config(cursor="")
            self.canvas_derecho.unbind("<Button-1>")
            self.canvas_derecho.unbind("<Motion>")

    def _activar_modo_region(self, on_release_callback: Callable):
        self.on_region_select_callback = on_release_callback
        self.canvas_derecho.config(cursor="tcross")
        self.canvas_derecho.bind("<ButtonPress-1>", self._on_press_region)
        self.canvas_derecho.bind("<B1-Motion>", self._on_drag_region)
        self.canvas_derecho.bind("<ButtonRelease-1>", self._on_release_region)

    def _on_press_region(self, event):
        self.region_start_coords = (self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y))
        self.feedback_rect_id = self.canvas_derecho.create_rectangle(*self.region_start_coords, *self.region_start_coords, outline="red", dash=(5, 2))

    def _on_drag_region(self, event):
        if not hasattr(self, 'region_start_coords') or not self.region_start_coords: return
        cur_x, cur_y = self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y)
        self.canvas_derecho.coords(self.feedback_rect_id, *self.region_start_coords, cur_x, cur_y)

    def _on_release_region(self, event):
        if not hasattr(self, 'region_start_coords') or not self.region_start_coords: return
        start_x_canvas, start_y_canvas = self.region_start_coords
        end_x_canvas, end_y_canvas = self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y)
        box_img = (int(min(start_x_canvas, end_x_canvas) / self.zoom_level), int(min(start_y_canvas, end_y_canvas) / self.zoom_level), int(max(start_x_canvas, end_x_canvas) / self.zoom_level), int(max(start_y_canvas, end_y_canvas) / self.zoom_level))
        
        if self.on_region_select_callback:
            self.on_region_select_callback(box_img)

        self.canvas_derecho.delete(self.feedback_rect_id)
        self._desactivar_modos()
        self.region_start_coords = None
    
    def _on_release_recorte(self, box: Tuple[int, int, int, int]):
        """Callback que se ejecuta al soltar el mouse en modo recorte."""
        if box[2] - box[0] > 0 and box[3] - box[1] > 0:
            recorte_pil = self.imagen_procesada.crop(box)
            self._mostrar_ventana_resultado(recorte_pil, "Resultado del Recorte")
        
    def _on_release_analisis(self, box: Tuple[int, int, int, int]):
        if box[2] - box[0] <= 0 or box[3] - box[1] <= 0: return
        region_pil = self.imagen_procesada.crop(box)
        pixeles = np.array(region_pil)
        promedio_rgb = np.mean(pixeles, axis=(0, 1))
        r, g, b = int(promedio_rgb[0]), int(promedio_rgb[1]), int(promedio_rgb[2])
        promedio_gris = int(0.299 * r + 0.587 * g + 0.114 * b)
        self.analisis_vars["total"].set(f"{pixeles.shape[0] * pixeles.shape[1]}")
        self.analisis_vars["r"].set(f"{r}")
        self.analisis_vars["g"].set(f"{g}")
        self.analisis_vars["b"].set(f"{b}")
        self.analisis_vars["gris"].set(f"{promedio_gris}")

    def _limpiar_resultados_analisis(self):
        for var in self.analisis_vars.values(): var.set("-")

    def _mostrar_ventana_resultado(self, imagen_pil: Image.Image, titulo: str):
        def guardar():
            self._guardar_imagen_pil(imagen_pil, f"Guardar {titulo}")
        DialogoResultado(self.root, imagen_pil, titulo, guardar)

    def _guardar_imagen_pil(self, imagen_pil: Image.Image, titulo_dialogo: str, parent_window=None):
        parent = parent_window if parent_window else self.root
        ruta_archivo = filedialog.asksaveasfilename(parent=parent, title=titulo_dialogo, defaultextension=".png", filetypes=self.FORMATOS_IMAGEN)
        if ruta_archivo:
            try:
                imagen_pil.save(ruta_archivo)
                messagebox.showinfo("Guardado Exitoso", f"Imagen guardada en:\n{ruta_archivo}", parent=parent)
                if parent_window: parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar la imagen.\nError: {e}", parent=parent)

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorDeImagenes(root)
    root.mainloop()