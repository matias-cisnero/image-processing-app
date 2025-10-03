# Librerias
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from typing import Optional, Tuple, Callable
import matplotlib.pyplot as plt
import webbrowser
import os

# Importaciones de código en archivos
from utils import requiere_imagen, refrescar_imagen
from ui_dialogs import (DialogoDimensiones, DialogoResultado, DialogoRecorteConAnalisis, DialogoGamma, DialogoUmbralizacion,
                        DialogoHistogramas, DialogoHistogramaDist, DialogoRuido, DialogoFiltro, Tooltip, DialogoDifusion,
                        DialogoLaplaciano, DialogoBilateral
                        )
from processing import (aplicar_negativo, aplicar_ecualizacion_histograma, aplicar_filtro,
                        crear_filtro_media, crear_filtro_mediana, crear_filtro_mediana_ponderada, crear_filtro_gaussiano, crear_filtro_realce,
                        crear_filtro_prewitt_x, crear_filtro_prewitt_y, crear_filtro_sobel_x, crear_filtro_sobel_y, aplicar_filtro_combinado,
                        restar_imagenes, aplicar_umbralizacion_iterativa
                        )

def abrir_github(event):
    webbrowser.open_new("https://github.com/matias-cisnero/procesamiento_imagenes")

def abrir_flaticon(event):
    webbrowser.open_new("https://www.flaticon.com/uicons")

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---

class EditorDeImagenes:
    GEOMETRIA_VENTANA = "1200x700+220+60"
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
        self.iconos = {}
        self._cargar_iconos()

        # Atajos de teclado
        self.root.bind("<Control-o>", self._cargar_imagen)
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
        panel_principal.grid_columnconfigure(2, minsize=1)
        panel_principal.grid_rowconfigure(0, weight=1)

        self._crear_visores_de_imagen(panel_principal)
        self._crear_panel_control_fijo(panel_principal)
        self._crear_panel_inferior()

    def _crear_menu(self):
        barra_menu = tk.Menu(self.root)
        self.root.config(menu=barra_menu)
        
        menu_archivo = tk.Menu(barra_menu, tearoff=0) # tk.Menu(barra_menu, tearoff=0, bg="#fcfdfd", fg="#7B7E83", activebackground="#cfd6e6", activeforeground="white", font=("Segoe UI", 10))
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cargar Imagen...", image=self.iconos['cargar'], compound="left", command=self._cargar_imagen, accelerator="Ctrl+O")
        menu_archivo.add_command(label="Guardar Imagen Como...", image=self.iconos['guardar'], compound="left", command=self._guardar_imagen_como, accelerator="Ctrl+S")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", image=self.iconos['salir'], compound="left", command=self.root.quit)
        
        menu_operadores_puntuales = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Operadores Puntuales", menu=menu_operadores_puntuales)
        menu_operadores_puntuales.add_command(label="Transformación Gamma", image=self.iconos['gamma'], compound="left", command=lambda: self._iniciar_dialogo(DialogoGamma))
        menu_operadores_puntuales.add_command(label="Umbralización", image=self.iconos['umbralizacion'], compound="left", command=lambda: self._iniciar_dialogo(DialogoUmbralizacion))
        menu_operadores_puntuales.add_command(label="Negativo", image=self.iconos['negativo'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_negativo))

        menu_histogramas = tk.Menu(barra_menu, tearoff=0)
        config_dist_gaussiano = {'titulo': "Histograma Gaussiano", 'param_label': "Desviación Estándar (σ):", 'distribucion': np.random.normal}
        config_dist_rayleigh = {'titulo': "Histograma Rayleigh", 'param_label': "Parámetro Xi (ξ):", 'distribucion': np.random.rayleigh}
        config_dist_exponencial = {'titulo': "Histograma Exponencial", 'param_label': "Lambda (λ):", 'distribucion': np.random.exponential}
        barra_menu.add_cascade(label="Histogramas", menu=menu_histogramas)
        menu_histogramas.add_command(label="Niveles de Gris y RGB", image=self.iconos['histograma'], compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramas))
        menu_histogramas.add_command(label="Ecualización", image=self.iconos['ecualizacion'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_ecualizacion_histograma, byn=True))
        menu_histogramas.add_separator()
        menu_histogramas.add_command(label="Generador Gaussiano", image=self.iconos['normal'], compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_gaussiano))
        menu_histogramas.add_command(label="Generador Rayleigh", image=self.iconos['rayleigh'], compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_rayleigh))
        menu_histogramas.add_command(label="Generador Exponencial", image=self.iconos['exponencial'], compound="left", command=lambda: self._iniciar_dialogo(DialogoHistogramaDist, config=config_dist_exponencial))

        menu_ruido = tk.Menu(barra_menu, tearoff=0)
        config_gaussiano = {'titulo': "Ruido Gaussiano", 'param_label': "Desviación Estándar (σ):", 'distribucion': np.random.normal, 'sal_y_pimienta': False, 'res': 1}
        config_rayleigh = {'titulo': "Ruido Rayleigh", 'param_label': "Parámetro Xi (ξ):", 'distribucion': np.random.rayleigh, 'sal_y_pimienta': False, 'res': 1}
        config_exponencial = {'titulo': "Ruido Exponencial", 'param_label': "Lambda (λ):", 'distribucion': np.random.exponential, 'sal_y_pimienta': False, 'res': 1}
        config_sal_y_pimienta = {'titulo': "Sal y Pimienta", 'param_label': "-", 'distribucion': np.random.normal, 'sal_y_pimienta': True, 'res': 2}
        barra_menu.add_cascade(label="Ruido", menu=menu_ruido)
        menu_ruido.add_command(label="Gaussiano", image=self.iconos['normal'], compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_gaussiano))
        menu_ruido.add_command(label="Rayleigh", image=self.iconos['rayleigh'], compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_rayleigh))
        menu_ruido.add_command(label="Exponencial", image=self.iconos['exponencial'], compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_exponencial))
        menu_ruido.add_command(label="Sal y Pimienta", image=self.iconos['sal_y_pimienta'], compound="left", command=lambda: self._iniciar_dialogo(DialogoRuido, config=config_sal_y_pimienta))
        #menu_ruido.add_command(label="Sal y Pimienta", image=self.icono_sal_y_pimienta, compound="left", command=lambda: self._iniciar_dialogo(DialogoRuidoSalYPimienta))

        menu_filtros = tk.Menu(barra_menu, tearoff=0)
        config_filtro_media = {'titulo': "Filtro de la Media", 'gaussiano': False, 'filtro': crear_filtro_media, 'modo': 0, 'mediana': False}
        config_filtro_gaussiano = {'titulo': "Filtro Gaussiano", 'gaussiano': True, 'filtro': crear_filtro_gaussiano, 'modo': 0, 'mediana': False}
        config_filtro_mediana = {'titulo': "Filtro de la Mediana", 'gaussiano': False, 'filtro': crear_filtro_mediana, 'modo': 2, 'mediana': True}
        config_filtro_mediana_ponderada = {'titulo': "Filtro de la Mediana ponderada", 'gaussiano': False, 'filtro': crear_filtro_mediana_ponderada, 'modo': 2, 'mediana': True}
        config_isotropico = {'titulo': "Difusión Isotrópica", 'isotropico': True}
        config_anisotropico = {'titulo': "Difusión Anisotrópica", 'isotropico': False}
        barra_menu.add_cascade(label="Filtros", menu=menu_filtros)
        menu_filtros.add_command(label="Media", image=self.iconos['media'], compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltro, config=config_filtro_media))
        menu_filtros.add_command(label="Gaussiano", image=self.iconos['normal'], compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltro, config=config_filtro_gaussiano))
        menu_filtros.add_separator()
        menu_filtros.add_command(label="Mediana", image=self.iconos['mediana'], compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltro, config=config_filtro_mediana))
        menu_filtros.add_command(label="Mediana Ponderada", image=self.iconos['mediana_ponderada'], compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltro, config=config_filtro_mediana_ponderada))
        menu_filtros.add_separator()
        menu_filtros.add_command(label="Difusión Isotrópica", image=self.iconos['sol'], compound="left", command=lambda: self._iniciar_dialogo(DialogoDifusion, config=config_isotropico))
        menu_filtros.add_command(label="Difusión Anisotrópica", image=self.iconos['sol'], compound="left", command=lambda: self._iniciar_dialogo(DialogoDifusion, config=config_anisotropico))
        menu_filtros.add_separator()
        menu_filtros.add_command(label="Filtro Bilateral", image=self.iconos['omega'], compound="left", command=lambda: self._iniciar_dialogo(DialogoBilateral))
        
        menu_bordes = tk.Menu(barra_menu, tearoff=0)
        config_filtro_realce = {'titulo': "Filtro Realce de bordes", 'gaussiano': False, 'filtro': crear_filtro_realce, 'modo': 0, 'mediana': False}
        config_laplaciano = {'titulo': "Método del Laplaciano", 'log': False}
        config_log = {'titulo': "Método del LoG", 'log': True}
        barra_menu.add_cascade(label="Bordes", menu=menu_bordes)
        menu_bordes.add_command(label="Realce de Bordes", image=self.iconos['borde'], compound="left", command=lambda: self._iniciar_dialogo(DialogoFiltro, config=config_filtro_realce))
        menu_bordes.add_separator()
        menu_bordes.add_command(label="Prewitt X", image=self.iconos['borde_x'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro, func_filtro=crear_filtro_prewitt_x, modo=1))
        menu_bordes.add_command(label="Prewitt Y", image=self.iconos['borde_y'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro, func_filtro=crear_filtro_prewitt_y, modo=1))
        menu_bordes.add_command(label="Módulo del gradiente (Prewitt)", image=self.iconos['gradiente'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro_combinado, func_filtro1=crear_filtro_prewitt_x, func_filtro2=crear_filtro_prewitt_y))
        menu_bordes.add_separator()
        menu_bordes.add_command(label="Sobel X", image=self.iconos['borde_x'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro, func_filtro=crear_filtro_sobel_x, modo=1))
        menu_bordes.add_command(label="Sobel Y", image=self.iconos['borde_y'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro, func_filtro=crear_filtro_sobel_y, modo=1))
        menu_bordes.add_command(label="Módulo del gradiente (Sobel)", image=self.iconos['gradiente'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_filtro_combinado, func_filtro1=crear_filtro_sobel_x, func_filtro2=crear_filtro_sobel_y))
        menu_bordes.add_separator()
        menu_bordes.add_command(label="Método del Laplaciano", image=self.iconos['laplaciano'], compound="left", command=lambda: self._iniciar_dialogo(DialogoLaplaciano, config=config_laplaciano))
        menu_bordes.add_command(label="LoG (Marr-Hildreth)", image=self.iconos['laplaciano'], compound="left", command=lambda: self._iniciar_dialogo(DialogoLaplaciano, config=config_log))

        menu_umbralizacion = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Umbralización", menu=menu_umbralizacion)
        menu_umbralizacion.add_command(label="Umbralización óptima iterativa", image=self.iconos['ciclo'], compound="left", command=lambda: self._aplicar_transformacion(self.imagen_procesada, aplicar_umbralizacion_iterativa, byn=True))
        menu_umbralizacion.add_command(label="Método de umbralización de Otsu", image=self.iconos['otsu'], compound="left")
        menu_umbralizacion.add_command(label="Segmentación de imágenes en color", image=self.iconos['recursos'], compound="left")

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
        panel_control = ttk.Frame(parent, padding=5)
        panel_control.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Botón 1: Volver a Original
        btn_volver = ttk.Button(panel_control, image=self.iconos['volver'], command=self._volver_imagen_original)
        btn_volver.grid(row=0, column=0, pady=4)
        Tooltip(widget=btn_volver, text="Volver a Original (Ctrl+Z)")

        # Botón 2: Convertir a Grises
        btn_grises = ttk.Button(panel_control, image=self.iconos['escala_grises'], command=self._escala_grises)
        btn_grises.grid(row=1, column=0, pady=4)
        Tooltip(widget=btn_grises, text="Convertir a escala de grises")

        # Botón 3: Recortar Región
        btn_recorte = ttk.Button(panel_control, image=self.iconos['recorte'], command=self._activar_modo_recorte)
        btn_recorte.grid(row=2, column=0, pady=4)
        Tooltip(widget=btn_recorte, text="Recortar una región")

        # Botón 4: Restar Imágenes
        btn_resta = ttk.Button(panel_control, image=self.iconos['resta_imagenes'], command=self._iniciar_resta)
        btn_resta.grid(row=3, column=0, pady=4)
        Tooltip(widget=btn_resta, text="Restar imagen")

        # Botón 5: Seleccionar Pixel
        btn_pixel = ttk.Button(panel_control, image=self.iconos['gotero'], command=self._activar_modo_seleccion)
        btn_pixel.grid(row=4, column=0, pady=4)
        Tooltip(widget=btn_pixel, text="Seleccionar y modificar pixel")
        
    def _crear_panel_inferior(self):
        footer_frame = ttk.Frame(self.root, padding=5)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        footer_frame.columnconfigure(0, weight=1)

        # --- 1. Frame Izquierdo: Herramientas ---

        frame_herramientas = ttk.Frame(footer_frame)
        frame_herramientas.grid(row=0, column=0, sticky="w")

        panel_info_pixel = ttk.Frame(frame_herramientas)
        panel_info_pixel.pack(pady=(0, 10))

        # 1. El label color
        ttk.Label(panel_info_pixel, text="Color:").grid(row=0, column=0, sticky="ns", padx=(0, 5))

        # 2. El preview de color
        self.color_preview = tk.Canvas(panel_info_pixel, width=20, height=20, bg="white", relief="sunken", borderwidth=1)
        self.color_preview.grid(row=0, column=1, sticky="ns", padx=(0, 5))

        # 3. El separator
        ttk.Separator(panel_info_pixel, orient='vertical').grid(row=0, column=2, sticky="ns")

        # 4. El grid con los valores R, G, B
        grid_rgb = ttk.Frame(panel_info_pixel)
        grid_rgb.grid(row=0, column=3, sticky="w", padx=(5, 0))
        
        pos = [(0, 1), (2, 3), (4, 5)]
        for i, canal in enumerate(self.CANALES_RGB):
            col = pos[i]
            ttk.Label(grid_rgb, text=f"{canal}:").grid(row=0, column=col[0], sticky="w")
            ttk.Entry(grid_rgb, textvariable=self.rgb_vars[canal], width=3).grid(row=0, column=col[1], padx=5)

        # --- 2. Frame Central: Créditos y Enlaces ---
        frame_creditos = ttk.Frame(footer_frame)
        frame_creditos.grid(row=0, column=0, sticky="e")
        
        label_github = ttk.Label(frame_creditos, text="GitHub", foreground="blue", cursor="hand2", image=self.iconos['github'], compound="left")
        label_github.pack(side=tk.LEFT, padx=5)
        label_github.bind("<Button-1>", abrir_github)

        label_creditos = ttk.Label(frame_creditos, text="Iconos por Flaticon", foreground="blue", cursor="hand2", image=self.iconos['flaticon'], compound="left")
        label_creditos.pack(side=tk.LEFT, padx=10)
        label_creditos.bind("<Button-1>", abrir_flaticon)

        # --- 3. Frame Derecho: Controles de Zoom ---
        frame_zoom = ttk.Frame(footer_frame)
        frame_zoom.grid(row=0, column=2, sticky="w")

        ttk.Label(frame_zoom, text="Zoom:").pack(side=tk.LEFT, padx=(5, 5))
        
        self.zoom_slider = ttk.Scale(frame_zoom, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, command=self._actualizar_zoom_desde_slider)
        self.zoom_slider.pack(side=tk.LEFT, padx=5)

        self.zoom_spinbox = ttk.Spinbox(frame_zoom, from_=self.ZOOM_MIN * 100, to=self.ZOOM_MAX * 100, textvariable=self.zoom_var, width=8, command=self._actualizar_zoom_desde_spinbox)
        self.zoom_spinbox.pack(side=tk.LEFT, padx=5)
        self.zoom_spinbox.bind("<Return>", self._actualizar_zoom_desde_spinbox)

    # En main.py, dentro de la clase EditorDeImagenes

    def _cargar_iconos(self):
        """
        Carga automáticamente todos los iconos .png de la carpeta 'icons'
        en el diccionario self.iconos.
        """
        icons_dir = "icons"
        if not os.path.isdir(icons_dir):
            print(f"Advertencia: No se encontró el directorio de iconos en '{icons_dir}'")
            return
        
        for filename in os.listdir(icons_dir):
            if filename.endswith(".png"):
                nombre_clave = os.path.splitext(filename)[0]
                ruta_completa = os.path.join(icons_dir, filename)
                
                try:
                    imagen = tk.PhotoImage(file=ruta_completa).subsample(5, 5)
                    self.iconos[nombre_clave] = imagen
                except tk.TclError as e:
                    print(f"Advertencia: No se pudo cargar el ícono '{filename}': {e}")


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

    # =============================((APLICAR_TRANSFORMACIÓN))================================

    @requiere_imagen
    @refrescar_imagen
    def _aplicar_transformacion(self, imagen, funcion, *args, byn=False, **kwargs,):
        if byn:
            imagen_np = np.array(imagen.convert('L')).astype(float)
            print("Transformo en byn!!")
        else:
            imagen_np = np.array(imagen.convert('RGB')).astype(float)
            print("Transformo en color!!")

        resultado_np = funcion(imagen_np, *args, **kwargs)

        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8')).convert('RGB')

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

    # ===================================((RUIDO))===========================================

    # Pasado a processing y ui_dialogs

    # ===================================((FILTROS))=========================================

    # Pasado a processing y ui_dialogs

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
            
            imagen_np1 = np.array(self.imagen_procesada.convert('RGB')).astype(float)
            imagen_np2 = np.array(img2.convert('RGB')).astype(float)
            
            resultado_np = restar_imagenes(imagen_np1, imagen_np2)

            resultado = Image.fromarray(resultado_np.astype('uint8')).convert('RGB')
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

    # --- Lógica de Carga y Guardado ---
    def _cargar_imagen(self, event=None):
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
        """
        Callback que se ejecuta al soltar el mouse.
        Ahora recorta Y analiza la región seleccionada.
        """
        if box[2] - box[0] <= 0 or box[3] - box[1] <= 0: return

        # 1. Recorta la imagen
        recorte_pil = self.imagen_procesada.crop(box)
        
        # 2. Analiza la misma región recortada
        pixeles = np.array(recorte_pil)
        promedio_rgb = np.mean(pixeles, axis=(0, 1))
        r = int(promedio_rgb[0])
        g = int(promedio_rgb[1])
        b = int(promedio_rgb[2])
        promedio_gris = int(0.299 * r + 0.587 * g + 0.114 * b)
        
        # 3. Guarda los datos en un diccionario para pasárselos al nuevo diálogo
        datos_analisis = {
            "Total Píxeles": f"{pixeles.shape[0] * pixeles.shape[1]}",
            "Promedio R": f"{r}",
            "Promedio G": f"{g}",
            "Promedio B": f"{b}",
            "Promedio Gris": f"{promedio_gris}"
        }

        # 4. Muestra el nuevo diálogo que contiene la imagen Y los datos
        self._mostrar_ventana_recorte_con_analisis(recorte_pil, datos_analisis)

    # --- Crear un nuevo método para mostrar el diálogo mejorado ---
    def _mostrar_ventana_recorte_con_analisis(self, imagen_pil: Image.Image, datos: dict):
        """Muestra el nuevo diálogo con la imagen recortada y los datos de análisis."""
        def guardar():
            self._guardar_imagen_pil(imagen_pil, "Guardar recorte como...")

        DialogoRecorteConAnalisis(
            parent=self.root,
            titulo="Recorte y Análisis",
            imagen_pil=imagen_pil,
            datos_analisis=datos,
            guardar_callback=guardar
        )

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
# from ttkthemes import ThemedTk
if __name__ == "__main__":
    root = tk.Tk() # root = ThemedTk(theme="breeze") # Para mejores visuales también theme="arc"
    app = EditorDeImagenes(root)
    root.mainloop()