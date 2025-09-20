import numpy as np

"""
Archivo con la lógica del procesamiento de las imágenes (solo trabaja con arrays de numpy)
"""

# ===============================((OPERADORES_PUNTUALES))================================

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

def aplicar_gamma(imagen_np: np.ndarray, gamma:float) -> np.ndarray:
    c = (255)**(1-gamma)
    resultado_np = c*(imagen_np**gamma)

    return resultado_np

def aplicar_umbralizacion(imagen_np: np.ndarray, umbral:int) -> np.ndarray:
    resultado_np = np.where(imagen_np >= umbral, 255, 0)

    return resultado_np

def aplicar_negativo(imagen_np: np.ndarray) -> np.ndarray:
    resultado_np = 255 - imagen_np

    return resultado_np