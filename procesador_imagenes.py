import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageChops
import numpy as np
from typing import Optional, Tuple, Callable

# --- DECORADORES (SIN @wraps) ---
def requiere_imagen(func: Callable) -> Callable:
    """
    Decorador que comprueba si existe una imagen procesada (`self.imagen_procesada`).
    Si no existe, muestra una advertencia y no ejecuta la función.
    """
    def wrapper(self, *args, **kwargs):
        if not self.imagen_procesada:
            messagebox.showwarning("Sin Imagen", "Esta operación requiere tener una imagen cargada.", parent=self.root)
            return None
        return func(self, *args, **kwargs)
    return wrapper

def refrescar_imagen(func: Callable) -> Callable:
    """
    Decorador que llama al método de actualización del display de imágenes
    (`_actualizar_display_imagenes`) después de que la función decorada se ejecute.
    """
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        # Solo refresca si la función no retornó explícitamente False
        if resultado is not False:
            self._actualizar_display_imagenes()
        return resultado
    return wrapper


# --- Cuadro de diálogo para solicitar dimensiones (sin cambios) ---
class DialogoDimensiones(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dimensiones de la Imagen RAW")
        self.transient(parent)
        self.grab_set()
        self.resultado = None

        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True)

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

        # --- Lógica para centrar la ventana ---
        self.update_idletasks() # Asegura que las dimensiones de la ventana estén calculadas
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        # --- Fin de la lógica de centrado ---

        self.ancho_entry.focus_set()
        self.wait_window(self)

    def _on_ok(self):
        try:
            ancho = int(self.ancho_var.get())
            alto = int(self.alto_var.get())
            if ancho <= 0 or alto <= 0:
                raise ValueError("Las dimensiones deben ser positivas.")
            self.resultado = (ancho, alto)
            self.destroy()
        except (ValueError, TypeError):
            messagebox.showerror("Error de Entrada", "Por favor, ingrese números enteros válidos y positivos.", parent=self)


class EditorDeImagenes:
    GEOMETRIA_VENTANA = "1200x700+200+50"
    FORMATOS_IMAGEN = [
        ("Imágenes Soportadas", "*.jpg *.jpeg *.png *.bmp *.pgm *.raw"),
        ("Archivo RAW", "*.raw"),
        ("Archivo PGM", "*.pgm"),
        ("Todos los archivos", "*.*")
    ]
    CANALES_RGB = ("R", "G", "B")
    ZOOM_MIN, ZOOM_MAX = 0.1, 3.0

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Procesador de Imágenes Avanzado")
        self.root.geometry(self.GEOMETRIA_VENTANA)

        self.imagen_original: Optional[Image.Image] = None
        self.imagen_procesada: Optional[Image.Image] = None
        self.pixel_seleccionado: Optional[Tuple[int, int]] = None
        self.modo_seleccion_pixel = False
        self.modo_seleccion_region = False
        self.region_start_coords = None
        self.feedback_rect_id = None
        self.on_region_select_callback: Optional[Callable] = None
        self.zoom_level = 1.0

        self.rgb_vars = {c: tk.StringVar(value="") for c in self.CANALES_RGB}
        self.zoom_var = tk.StringVar()
        self.instruccion_var = tk.StringVar()
        self.analisis_vars = {"total": tk.StringVar(value="-"), "r": tk.StringVar(value="-"), "g": tk.StringVar(value="-"), "b": tk.StringVar(value="-"), "gris": tk.StringVar(value="-")}
        
        self.paneles = {}
        self.panel_herramientas_actual = None

        self._setup_ui()
        self._vincular_eventos()
        self._cambiar_panel_herramienta("instruccion", "Bienvenido", "Seleccione una herramienta del menú para comenzar.")

    # --- SECCIÓN 1: UI ---
    def _setup_ui(self):
        self._crear_menu()
        panel_principal = tk.Frame(self.root)
        panel_principal.pack(fill=tk.BOTH, expand=True)
        panel_principal.grid_columnconfigure(0, weight=2)
        panel_principal.grid_columnconfigure(1, weight=2)
        panel_principal.grid_columnconfigure(2, weight=1)
        panel_principal.grid_rowconfigure(0, weight=1)
        self._crear_visores_de_imagen(panel_principal)
        self._crear_contenedor_herramientas(panel_principal)
        self._crear_controles_zoom()
        self.paneles["pixel"] = self._crear_panel_pixel(self.contenedor_herramientas)
        self.paneles["analisis"] = self._crear_panel_analisis(self.contenedor_herramientas)
        self.paneles["instruccion"] = self._crear_panel_instrucciones(self.contenedor_herramientas)
        # --- PASO 1: REGISTRAR EL NUEVO PANEL ---
        self.paneles["plantilla"] = self._crear_panel_plantilla(self.contenedor_herramientas)


    def _crear_menu(self):
        barra_menu = tk.Menu(self.root)
        self.root.config(menu=barra_menu)
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cargar Imagen...", command=self._cargar_imagen)
        menu_archivo.add_command(label="Guardar Imagen Como...", command=self._guardar_imagen_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menu_herramientas = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Herramientas", menu=menu_herramientas)
        submenu_edicion = tk.Menu(menu_herramientas, tearoff=0)
        menu_herramientas.add_cascade(label="Edición e Información", menu=submenu_edicion)
        submenu_edicion.add_command(label="Seleccionar Píxel", command=self._iniciar_seleccion_pixel)
        submenu_edicion.add_command(label="Recortar Región", command=self._iniciar_recorte_region)
        submenu_edicion.add_separator()
        submenu_edicion.add_command(label="Analizar Región", command=self._iniciar_analisis_region)
        menu_herramientas.add_command(label="Restar Imágenes", command=self._restar_imagenes)
        menu_herramientas.add_separator()
        # --- PASO 2: AÑADIR LA HERRAMIENTA AL MENÚ ---
        menu_herramientas.add_command(label="Herramienta de Plantilla", command=self._iniciar_herramienta_plantilla)


    def _crear_visores_de_imagen(self, parent: tk.Frame):
        frame_visores = tk.Frame(parent)
        frame_visores.grid(row=0, column=0, columnspan=2, sticky="nsew")
        frame_visores.grid_rowconfigure(0, weight=1)
        frame_visores.grid_columnconfigure(0, weight=1)
        frame_visores.grid_columnconfigure(1, weight=1)
        self.canvas_izquierdo = self._crear_panel_canvas(frame_visores, 0, "Imagen Original")
        self.canvas_derecho = self._crear_panel_canvas(frame_visores, 1, "Imagen Modificada")
        scroll_y = ttk.Scrollbar(frame_visores, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_visores, orient=tk.HORIZONTAL)
        def _scroll_y_view(*args):
            self.canvas_izquierdo.yview(*args)
            self.canvas_derecho.yview(*args)
        def _scroll_x_view(*args):
            self.canvas_izquierdo.xview(*args)
            self.canvas_derecho.xview(*args)
        scroll_y.config(command=_scroll_y_view)
        scroll_x.config(command=_scroll_x_view)
        self.canvas_izquierdo.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.canvas_derecho.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.grid(row=0, column=2, sticky="ns")
        scroll_x.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _crear_panel_canvas(self, parent: tk.Frame, col: int, titulo: str) -> tk.Canvas:
        frame = ttk.Labelframe(parent, text=titulo)
        frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        canvas = tk.Canvas(frame, bg="gray")
        canvas.pack(fill=tk.BOTH, expand=True)
        return canvas

    def _crear_contenedor_herramientas(self, parent: tk.Frame):
        self.contenedor_herramientas = ttk.Labelframe(parent, text="Herramienta")
        self.contenedor_herramientas.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=5)

    def _crear_controles_zoom(self):
        zoom_frame = ttk.Labelframe(self.root, text="Zoom")
        zoom_frame.pack(anchor="s", fill=tk.X, padx=10, pady=5)
        ttk.Label(zoom_frame, text=f"{self.ZOOM_MIN*100:.0f}%").pack(side=tk.LEFT, padx=(5,0))
        self.zoom_slider = ttk.Scale(zoom_frame, from_=self.ZOOM_MIN, to=self.ZOOM_MAX, orient=tk.HORIZONTAL, command=self._actualizar_zoom_desde_slider)
        self.zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(zoom_frame, text=f"{self.ZOOM_MAX*100:.0f}%").pack(side=tk.LEFT, padx=(0,5))
        self.zoom_spinbox = ttk.Spinbox(zoom_frame, from_=self.ZOOM_MIN*100, to=self.ZOOM_MAX*100, textvariable=self.zoom_var, width=8, command=self._actualizar_zoom_desde_spinbox)
        self.zoom_spinbox.pack(side=tk.RIGHT, padx=5)
        self.zoom_spinbox.bind("<Return>", self._actualizar_zoom_desde_spinbox)

    def _crear_panel_pixel(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent)
        rgb_frame = ttk.Frame(frame)
        rgb_frame.pack(pady=10, padx=5, fill=tk.X)
        for i, canal in enumerate(self.CANALES_RGB):
            ttk.Label(rgb_frame, text=f"{canal}:").grid(row=i, column=0, sticky="w")
            ttk.Entry(rgb_frame, textvariable=self.rgb_vars[canal], width=5).grid(row=i, column=1, padx=5)
        self.color_preview = tk.Canvas(rgb_frame, width=40, height=40, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.color_preview.grid(row=0, column=2, rowspan=3, padx=10)
        return frame

    def _crear_panel_analisis(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=10)
        ttk.Label(frame, text="Total de Píxeles:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(frame, textvariable=self.analisis_vars["total"]).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=1, columnspan=2, sticky="ew", pady=5)
        ttk.Label(frame, text="Promedio RGB:", font=("", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5,2))
        ttk.Label(frame, text="R:").grid(row=3, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.analisis_vars["r"]).grid(row=3, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="G:").grid(row=4, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.analisis_vars["g"]).grid(row=4, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="B:").grid(row=5, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.analisis_vars["b"]).grid(row=5, column=1, sticky="w", padx=5)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=6, columnspan=2, sticky="ew", pady=5)
        ttk.Label(frame, text="Nivel de Gris Prom.:").grid(row=7, column=0, sticky="w", pady=2)
        ttk.Label(frame, textvariable=self.analisis_vars["gris"]).grid(row=7, column=1, sticky="w", padx=5)
        return frame

    def _crear_panel_instrucciones(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=10)
        ttk.Label(frame, textvariable=self.instruccion_var, wraplength=220, justify=tk.LEFT).pack(fill=tk.BOTH, expand=True)
        return frame

    def _cambiar_panel_herramienta(self, nombre_panel: str, titulo: str = "Herramienta", texto_instruccion: Optional[str] = None):
        if self.panel_herramientas_actual:
            self.panel_herramientas_actual.pack_forget()
        panel_nuevo = self.paneles.get(nombre_panel)
        if panel_nuevo:
            self.contenedor_herramientas.config(text=titulo)
            if nombre_panel == "instruccion" and texto_instruccion:
                self.instruccion_var.set(texto_instruccion)
            panel_nuevo.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.panel_herramientas_actual = panel_nuevo

    # --- PLANTILLA PARA NUEVA HERRAMIENTA ---

    def _crear_panel_plantilla(self, parent) -> ttk.Frame:
        """Crea el panel de la interfaz de usuario para la herramienta de plantilla."""
        frame = ttk.Frame(parent, padding=10)
        
        # Widgets específicos para tu herramienta (ej. sliders, entries, etc.)
        info_label = ttk.Label(
            frame, 
            text="Este es un panel para una nueva herramienta. Presiona el botón para aplicar la transformación.", 
            wraplength=220, 
            justify=tk.LEFT
        )
        info_label.pack(fill=tk.X, pady=(0, 15))

        # Botón para ejecutar la lógica principal
        apply_button = ttk.Button(
            frame, 
            text="Aplicar Transformación", 
            command=self._aplicar_transformacion_plantilla
        )
        apply_button.pack(fill=tk.X, ipady=5)

        return frame

    @requiere_imagen
    def _iniciar_herramienta_plantilla(self):
        """Función llamada desde el menú para activar la herramienta."""
        self._cambiar_panel_herramienta("plantilla", "Herramienta de Plantilla")

    @refrescar_imagen
    def _aplicar_transformacion_plantilla(self):
        """
        Lógica principal de la herramienta.
        Convierte la imagen a NumPy, permite la edición y la revierte a PIL.
        """
        print("Aplicando transformación de plantilla...")
        
        # 1. Convertir la imagen procesada (PIL) a un array de NumPy
        imagen_np = np.array(self.imagen_procesada)

        # ------------------------------------------------------------------
        # --- AQUÍ VA TU LÓGICA DE EDICIÓN ---
        #
        # Trabaja con la variable `imagen_np`.
        # Ejemplo: invertir los colores de la imagen.
        # imagen_np = 255 - imagen_np
        # 
        # Por ahora, no hacemos nada para demostrar la plantilla.
        # ------------------------------------------------------------------

        # 3. Convertir el array de NumPy de vuelta a una imagen PIL
        imagen_modificada_pil = Image.fromarray(imagen_np.astype('uint8'), 'RGB')

        # 4. Actualizar la imagen procesada con el resultado
        self.imagen_procesada = imagen_modificada_pil
        
        print("Transformación completada.")

    # --- FIN DE LA PLANTILLA ---

    # --- SECCIÓN 2: Lógica de Carga y Manejo de Eventos ---

    def _abrir_imagen(self, titulo: str = "Seleccionar Imagen") -> Optional[Image.Image]:
        """Abre un archivo de imagen (RAW o estándar) y lo retorna como PIL.Image."""
        ruta = filedialog.askopenfilename(title=titulo, filetypes=self.FORMATOS_IMAGEN)
        if not ruta:
            return None
        
        try:
            if ruta.lower().endswith(".raw"):
                dialogo = DialogoDimensiones(self.root)
                if not dialogo.resultado:
                    return None
                ancho, alto = dialogo.resultado
                return self._leer_raw_como_pil(ruta, ancho, alto)
            else:
                return Image.open(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen.\n{e}")
            return None

    def _cargar_imagen(self):
        img = self._abrir_imagen("Cargar Imagen")
        if img:
            self._finalizar_carga_imagen(img)

    def _leer_raw_como_pil(self, ruta: str, ancho: int, alto: int) -> Optional[Image.Image]:
        """Lee un archivo RAW y lo convierte a un objeto PIL.Image, retornándolo."""
        try:
            total_pixeles = ancho * alto
            datos_raw = np.fromfile(ruta, dtype=np.uint8, count=total_pixeles)

            if datos_raw.size < total_pixeles:
                messagebox.showwarning("Error de Tamaño",
                    f"El archivo es más pequeño de lo esperado para las dimensiones {ancho}x{alto}.\n"
                    "La imagen podría mostrarse incorrectamente.", parent=self.root)
                datos_raw.resize(total_pixeles, refcheck=False)

            imagen_array = datos_raw.reshape((alto, ancho))
            return Image.fromarray(imagen_array, mode='L')
        except Exception as e:
            messagebox.showerror("Error al Leer RAW", f"No se pudo procesar el archivo RAW.\nError: {e}", parent=self.root)
            return None

    def _finalizar_carga_imagen(self, imagen_pil: Image.Image):
        self.imagen_original = imagen_pil.convert("RGB")
        self.imagen_procesada = self.imagen_original.copy()
        self._ajustar_zoom_inicial()
        
    @requiere_imagen
    def _restar_imagenes(self):
        self._cambiar_panel_herramienta("instruccion", "Restar Imágenes", "Seleccione la segunda imagen.")

        img2 = self._abrir_imagen("Seleccionar imagen a restar")
        if not img2:
            return
        
        img1 = self.imagen_procesada.copy()
        img2 = img2.convert("RGB")
        
        if img1.size != img2.size:
            messagebox.showerror("Error de Dimensiones", f"Las imágenes deben tener el mismo tamaño.\n\nActual: {img1.size}\nSeleccionada: {img2.size}")
            return
        
        resultado = ImageChops.subtract(img1, img2)
        self._mostrar_ventana_resultado(resultado, "Resultado de la Resta")
            
    def _vincular_eventos(self):
        for var in self.rgb_vars.values():
            var.trace_add("write", self._aplicar_cambio_color_en_vivo)

    @requiere_imagen
    def _guardar_imagen_como(self):
        self._guardar_imagen_pil(self.imagen_procesada, "Guardar imagen principal")

    def _actualizar_display_imagenes(self):
        if not self.imagen_original: return
        w, h = self.imagen_original.size
        w_zoom, h_zoom = int(w * self.zoom_level), int(h * self.zoom_level)
        for canvas, pil_image in [(self.canvas_izquierdo, self.imagen_original), (self.canvas_derecho, self.imagen_procesada)]:
            if pil_image: # Asegurarse que la imagen existe
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
        nuevo_nivel = float(valor_str)
        self.zoom_level = nuevo_nivel
        self.zoom_var.set(f"{nuevo_nivel * 100:.1f}%")
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

    @requiere_imagen
    def _iniciar_seleccion_pixel(self):
        self._cambiar_panel_herramienta("pixel", "Edición de Píxel")
        self._activar_modo_seleccion()

    @requiere_imagen
    def _iniciar_recorte_region(self):
        texto = "Arrastre el ratón sobre la imagen derecha para seleccionar el área a recortar."
        self._cambiar_panel_herramienta("instruccion", "Recortar Región", texto)
        self._activar_modo_region(self._on_release_recorte)

    @requiere_imagen
    def _iniciar_analisis_region(self):
        self._limpiar_resultados_analisis()
        self._cambiar_panel_herramienta("analisis", "Análisis de Región")
        self._activar_modo_region(self._on_release_analisis)

    def _activar_modo_region(self, on_release_callback: Callable):
        self.on_region_select_callback = on_release_callback
        self.modo_seleccion_region = True
        self.canvas_derecho.config(cursor="tcross")
        self.canvas_derecho.bind("<ButtonPress-1>", self._on_press_region)
        self.canvas_derecho.bind("<B1-Motion>", self._on_drag_region)
        self.canvas_derecho.bind("<ButtonRelease-1>", self._on_release_region)

    def _desactivar_modo_region(self):
        self.modo_seleccion_region = False
        self.canvas_derecho.config(cursor="")
        self.canvas_derecho.unbind("<ButtonPress-1>")
        self.canvas_derecho.unbind("<B1-Motion>")
        self.canvas_derecho.unbind("<ButtonRelease-1>")
        if self.feedback_rect_id:
            self.canvas_derecho.delete(self.feedback_rect_id)
        self.feedback_rect_id = None
        self.region_start_coords = None
        self.on_region_select_callback = None

    def _on_release_recorte(self, box: Tuple[int, int, int, int]):
        if box[2] - box[0] > 0 and box[3] - box[1] > 0:
            recorte_pil = self.imagen_procesada.crop(box)
            self._mostrar_ventana_resultado(recorte_pil, "Vista Previa del Recorte")

    def _on_release_analisis(self, box: Tuple[int, int, int, int]):
        if box[2] - box[0] <= 0 or box[3] - box[1] <= 0: return
        region_pil = self.imagen_procesada.crop(box)
        pixeles = np.array(region_pil)
        total_pixeles = pixeles.shape[0] * pixeles.shape[1]
        promedio_rgb = np.mean(pixeles, axis=(0, 1))
        r, g, b = int(promedio_rgb[0]), int(promedio_rgb[1]), int(promedio_rgb[2])
        promedio_gris = int(0.299 * r + 0.587 * g + 0.114 * b)
        self.analisis_vars["total"].set(f"{total_pixeles}")
        self.analisis_vars["r"].set(f"{r}")
        self.analisis_vars["g"].set(f"{g}")
        self.analisis_vars["b"].set(f"{b}")
        self.analisis_vars["gris"].set(f"{promedio_gris}")

    def _limpiar_resultados_analisis(self):
        for var in self.analisis_vars.values():
            var.set("-")

    def _activar_modo_seleccion(self):
        self.pixel_seleccionado = None
        self.modo_seleccion_pixel = True
        self.canvas_derecho.config(cursor="crosshair")
        self.canvas_derecho.bind("<Button-1>", self._fijar_pixel_seleccionado)
        self.canvas_derecho.bind("<Motion>", self._mostrar_info_pixel_hover)

    def _desactivar_modo_seleccion(self):
        self.modo_seleccion_pixel = False
        self.canvas_derecho.config(cursor="")
        self.canvas_derecho.unbind("<Button-1>")
        self.canvas_derecho.unbind("<Motion>")

    @requiere_imagen
    def _mostrar_info_pixel_hover(self, event):
        if not self.modo_seleccion_pixel: return
        img_x = int(self.canvas_derecho.canvasx(event.x) / self.zoom_level)
        img_y = int(self.canvas_derecho.canvasy(event.y) / self.zoom_level)
        width, height = self.imagen_procesada.size
        if 0 <= img_x < width and 0 <= img_y < height:
            r, g, b = self.imagen_procesada.getpixel((img_x, img_y))
            color_hex = f'#{r:02x}{g:02x}{b:02x}'
            self.color_preview.config(bg=color_hex)
            self.rgb_vars["R"].set(str(r))
            self.rgb_vars["G"].set(str(g))
            self.rgb_vars["B"].set(str(b))

    @requiere_imagen
    def _fijar_pixel_seleccionado(self, event):
        img_x = int(self.canvas_derecho.canvasx(event.x) / self.zoom_level)
        img_y = int(self.canvas_derecho.canvasy(event.y) / self.zoom_level)
        width, height = self.imagen_procesada.size
        if 0 <= img_x < width and 0 <= img_y < height:
            self.pixel_seleccionado = (img_x, img_y)
            self._desactivar_modo_seleccion()

    @refrescar_imagen
    def _aplicar_cambio_color_en_vivo(self, *args):
        if not self.pixel_seleccionado: return False
        try:
            r, g, b = (int(self.rgb_vars[c].get()) for c in self.CANALES_RGB)
            if not all(0 <= val <= 255 for val in (r, g, b)): return False
            
            self.imagen_procesada.putpixel(self.pixel_seleccionado, (r, g, b))
            self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
        except ValueError:
            return False # No refrescar si el valor es inválido (ej. "abc")

    def _on_press_region(self, event):
        self.region_start_coords = (self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y))
        self.feedback_rect_id = self.canvas_derecho.create_rectangle(*self.region_start_coords, *self.region_start_coords, outline="red", dash=(5, 2))

    def _on_drag_region(self, event):
        if not self.region_start_coords: return
        cur_x, cur_y = self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y)
        self.canvas_derecho.coords(self.feedback_rect_id, *self.region_start_coords, cur_x, cur_y)

    def _on_release_region(self, event):
        if not self.region_start_coords: return
        start_x_canvas, start_y_canvas = self.region_start_coords
        end_x_canvas, end_y_canvas = self.canvas_derecho.canvasx(event.x), self.canvas_derecho.canvasy(event.y)
        box_img = (
            int(min(start_x_canvas, end_x_canvas) / self.zoom_level), 
            int(min(start_y_canvas, end_y_canvas) / self.zoom_level), 
            int(max(start_x_canvas, end_x_canvas) / self.zoom_level), 
            int(max(start_y_canvas, end_y_canvas) / self.zoom_level)
        )
        if self.on_region_select_callback:
            self.on_region_select_callback(box_img)
        self._desactivar_modo_region()

    def _mostrar_ventana_resultado(self, imagen_pil: Image.Image, titulo: str):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.transient(self.root)
        
        img_tk = ImageTk.PhotoImage(imagen_pil)
        label_imagen = ttk.Label(ventana, image=img_tk)
        label_imagen.image_ref = img_tk
        label_imagen.pack(padx=10, pady=10)
        
        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(pady=5, padx=10, fill=tk.X)
        
        def guardar_y_cerrar():
            self._guardar_imagen_pil(imagen_pil, f"Guardar {titulo}")
            ventana.destroy()
            
        ttk.Button(frame_botones, text="Guardar...", command=guardar_y_cerrar).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(frame_botones, text="Cerrar", command=ventana.destroy).pack(side=tk.RIGHT, expand=True, padx=5)

        # --- Lógica para centrar la ventana ---
        ventana.update_idletasks()
        width = ventana.winfo_width()
        height = ventana.winfo_height()
        x = (ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana.winfo_screenheight() // 2) - (height // 2)
        ventana.geometry(f'{width}x{height}+{x}+{y}')
        # --- Fin de la lógica de centrado ---

        ventana.grab_set()

    def _guardar_imagen_pil(self, imagen_pil: Image.Image, titulo_dialogo: str):
        ruta_archivo = filedialog.asksaveasfilename(parent=self.root, title=titulo_dialogo, defaultextension=".png", filetypes=self.FORMATOS_IMAGEN)
        if ruta_archivo:
            try:
                imagen_pil.save(ruta_archivo)
                messagebox.showinfo("Guardado Exitoso", f"Imagen guardada en:\n{ruta_archivo}", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar la imagen.\nError: {e}", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorDeImagenes(root)
    root.mainloop()
