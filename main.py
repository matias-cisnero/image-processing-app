# Librerias
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageChops
import numpy as np
from typing import Optional, Tuple, Callable

# Importaciones de código en archivos
from utils import  requiere_imagen, refrescar_imagen
from ui_dialogs import DialogoBase, DialogoDimensiones, DialogoResultado, DialogoHerramienta, DialogoGamma, DialogoUmbralizacion, DialogoRuido, DialogoRuidoGaussiano

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---

class EditorDeImagenes:
    GEOMETRIA_VENTANA = "1200x700+200+50"
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
        menu_archivo.add_command(label="Cargar Imagen...", command=self._cargar_imagen)
        menu_archivo.add_command(label="Guardar Imagen Como...", command=self._guardar_imagen_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        menu_operadores_puntuales = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Operadores Puntuales", menu=menu_operadores_puntuales)
        menu_operadores_puntuales.add_command(label="Transformación Gamma", command=lambda: self._iniciar_dialogo(DialogoGamma))
        menu_operadores_puntuales.add_command(label="Umbralización", command=lambda: self._iniciar_dialogo(DialogoUmbralizacion))
        menu_operadores_puntuales.add_command(label="Negativo", command=self._aplicar_negativo)

        menu_histogramas = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Histogramas", menu=menu_histogramas)
        menu_histogramas.add_command(label="Niveles de Gris")#, command=self._aplicar_negativo)
        menu_histogramas.add_command(label="RGB")#, command=self._aplicar_negativo)
        menu_histogramas.add_command(label="Ecualización")#, command=self._aplicar_negativo)
        menu_histogramas.add_command(label="Números Aleatorios")#, command=self._aplicar_negativo)

        menu_ruido = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ruido", menu=menu_ruido)
        menu_ruido.add_command(label="Gaussiano", command=lambda: self._iniciar_dialogo(DialogoRuidoGaussiano))
        menu_ruido.add_command(label="Rayleigh")#, command=self._aplicar_negativo)
        menu_ruido.add_command(label="Exponencial")#, command=self._aplicar_negativo)
        menu_ruido.add_command(label="Sal y Pimienta")#, command=self._aplicar_negativo)

        menu_filtros = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Filtros", menu=menu_filtros)
        menu_filtros.add_command(label="Media")#, command=self._aplicar_negativo)
        menu_filtros.add_command(label="Mediana")#, command=self._aplicar_negativo)
        menu_filtros.add_command(label="Mediana Ponderada")#, command=self._aplicar_negativo)
        menu_filtros.add_command(label="Gauss")#, command=self._aplicar_negativo)
        menu_filtros.add_command(label="Realce de Bordes")#, command=self._aplicar_negativo)

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
        
        frame_pixel = ttk.Labelframe(panel_control, text="Edición de Píxel", padding=10)
        frame_pixel.pack(fill=tk.X, pady=5)
        
        pixel_grid = ttk.Frame(frame_pixel)
        pixel_grid.pack(fill=tk.X)
        self.color_preview = tk.Canvas(pixel_grid, width=40, height=40, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.color_preview.grid(row=0, column=2, rowspan=3, padx=(10, 0))
        for i, canal in enumerate(self.CANALES_RGB):
            ttk.Label(pixel_grid, text=f"{canal}:").grid(row=i, column=0, sticky="w")
            ttk.Entry(pixel_grid, textvariable=self.rgb_vars[canal], width=5).grid(row=i, column=1, padx=5)
        
        ttk.Button(frame_pixel, text="Activar Selección de Píxel", command=self._activar_modo_seleccion).pack(fill=tk.X, pady=(10,0))

        frame_recorte = ttk.Labelframe(panel_control, text="Recortar Región", padding=10)
        frame_recorte.pack(fill=tk.X, pady=5)
        ttk.Button(frame_recorte, text="Activar Selección para Recorte", command=self._activar_modo_recorte).pack(fill=tk.X)

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
        
        ttk.Button(frame_analisis, text="Activar Análisis de Región", command=self._activar_modo_analisis).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10,0))

        frame_resta_imagenes = ttk.Labelframe(panel_control, text="Resta de Imagenes", padding=10)
        frame_resta_imagenes.pack(fill=tk.X, pady=5)

        ttk.Label(frame_resta_imagenes, text="(De igual tamaño)").grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10,0))
        ttk.Button(frame_resta_imagenes, text="Restar Imagenes", command=self._iniciar_resta).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))

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
    def _iniciar_dialogo(self, dialogo_clase):
        """
        Método genérico para abrir cualquier diálogo de herramienta que necesite
        una referencia a la app principal.
        """
        #print("Sí, jeje, funciona")
        dialogo = dialogo_clase(self.root, self)

    # --- Cancelar Cambio

    @refrescar_imagen
    def _cancelar_cambio(self, imagen):
        self.imagen_procesada = imagen

    # ===============================((OPERADORES_PUNTUALES))================================
    
    # --- Gamma

    @refrescar_imagen
    def _aplicar_gamma(self, imagen, gamma):
        imagen_np = np.array(imagen)

        c = (255)**(1-gamma)
        resultado_np = c*(imagen_np**gamma)

        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8'))

    # --- Umbralización

    @refrescar_imagen
    def _aplicar_umbralizacion(self, imagen, umbral):
        imagen_np = np.array(imagen)

        resultado_np = np.where(imagen_np >= umbral, 255, 0)

        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8'))
    
    # --- Negativo
    
    @requiere_imagen
    @refrescar_imagen
    def _aplicar_negativo(self):
        imagen_np = np.array(self.imagen_procesada)
        #print(f"Cantidad de pixeles en la imágen {imagen_np.size}")
        #print(f"Tamaño de la imágen {imagen_np.shape}")
        resultado_np = 255 - imagen_np
        self.imagen_procesada = Image.fromarray(resultado_np.astype('uint8'))
    
    # =============================((NUMEROS_ALEATORIOS))====================================

    # --- 

    # ================================((HISTOGRAMAS))========================================

    # --- Niveles de Gris

    # --- RGB

    # --- Ecualización

    # --- Números Aleatorios

    # ===================================((RUIDO))===========================================

    # -- Aditivo y Multiplicativo

    @refrescar_imagen
    def _aplicar_ruido(self, imagen, tipo, vector_ruido, d):
        # Transformar la imágen en un formato adecuado
        imagen_np = np.array(imagen).astype(float)
        m, n = imagen_np.shape[:2] # Esto es para quedarme con 256 x 256 e ignorar los 3 canales rgb

        # Elección aleatoria de num_contaminados pixels en la imágen
        num_contaminados = int((d * (m * n)) / 100)
        D = np.unravel_index(np.random.choice(m * n, num_contaminados, replace=False),(m, n))

        # Generar la imagen contaminada I_c
        if tipo == "Aditivo":
            resultado_np = imagen_np + vector_ruido
        elif tipo == "Multiplicativo":
            resultado_np = imagen_np * vector_ruido
        
        resultado_np = np.clip(resultado_np, 0, 255).astype(np.uint8)
        self.imagen_procesada = Image.fromarray(resultado_np)

        # ------------------------------------------
        #   Tengo que resolver lo de los 3 canales
        # ------------------------------------------

    # --- Gaussiano

    def _ruido_gaussiano(self, sigma, d):
        imagen_np = np.array(self.imagen_procesada)

        m, n = imagen_np.shape[:2]
        num_contaminados = int((d * (m * n)) / 100)
        #print(f"Shape de imagen: {imagen_np.shape}")

        # Generar los num_contaminados valores aleatorios con dist gauss (en este caso)
        vector_aleatorio = np.random.normal(loc=0, scale=sigma, size=num_contaminados)

        return vector_aleatorio

    # --- Rayleigh

    # --- Exponencial

    # --- Gas y Pimienta

    # ===================================((FILTROS))=========================================

    # --- Media

    # --- Mediana

    # --- Mediana Ponderada

    # --- Gauss

    # --- Realce de Bordes

    # ===========================((HERRAMIENTAS_GENERALES))==================================

    @requiere_imagen
    def _iniciar_resta(self):
        ruta_img2 = filedialog.askopenfilename(title="Seleccionar imagen a restar", filetypes=self.FORMATOS_IMAGEN)
        if not ruta_img2: return

        try:
            img2 = Image.open(ruta_img2).convert("RGB")
            if self.imagen_procesada.size != img2.size:
                messagebox.showerror("Error de Dimensiones", "Las imágenes deben tener el mismo tamaño.")
                return
            
            resultado = ImageChops.subtract(self.imagen_procesada, img2)
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
    def _guardar_imagen_como(self):
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

