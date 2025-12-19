import numpy as np

def escalar_255(imagen_np: np.ndarray) -> np.ndarray:
    """
    Escala linealmente un array de numpy al rango [0, 255].
    """
    min_val = np.min(imagen_np)
    max_val = np.max(imagen_np)
    if max_val == min_val:
        return np.zeros_like(imagen_np, dtype=np.uint8)
    array_normalizado = 255 * (imagen_np - min_val) / (max_val - min_val)
    return array_normalizado.astype(np.uint8)

def restar_imagenes(imagen_np1: np.ndarray, imagen_np2: np.ndarray) -> np.ndarray:
    resultado_np = imagen_np1 - imagen_np2

    resultado_np = escalar_255(resultado_np)
    return resultado_np