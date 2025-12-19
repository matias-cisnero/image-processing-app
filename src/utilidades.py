from tkinter import messagebox
from typing import Callable
import os
import sys
import tkinter as tk

# --- DECORADORES ---
def requiere_imagen(func: Callable) -> Callable:
    """Decorador que comprueba si existe una imagen cargada."""
    def wrapper(self, *args, **kwargs):
        if not self.imagen_procesada:
            messagebox.showwarning("Sin Imagen", "Esta operación requiere tener una imagen cargada.", parent=self.root)
            return None
        return func(self, *args, **kwargs)
    return wrapper

def refrescar_imagen(func: Callable) -> Callable:
    """Decorador que refresca el display después de una acción."""
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        if resultado is not False:
            self._actualizar_display_imagenes()
        return resultado
    return wrapper

def resource_path(relative_path):
    """
    Devuelve la ruta absoluta del recurso, compatible con PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def cargar_iconos(ruta= "icons") -> dict:
        """
        Carga automáticamente todos los iconos .png de la carpeta 'icons'
        en un diccionario.
        """
        icons_dir = resource_path(ruta)
        if not os.path.isdir(icons_dir):
            print(f"Advertencia: No se encontró el directorio de iconos en '{icons_dir}'")
            return
        
        iconos = {}
        for filename in os.listdir(icons_dir):
            if filename.endswith(".png"):
                nombre_clave = os.path.splitext(filename)[0]
                ruta_completa = os.path.join(icons_dir, filename)
                
                try:
                    imagen = tk.PhotoImage(file=ruta_completa).subsample(4, 4)
                    iconos[nombre_clave] = imagen
                except tk.TclError as e:
                    print(f"Advertencia: No se pudo cargar el ícono '{filename}': {e}")
        return iconos

