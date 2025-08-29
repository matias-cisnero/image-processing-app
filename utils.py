from tkinter import messagebox
from typing import Callable

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