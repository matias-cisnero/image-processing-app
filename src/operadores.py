import numpy as np
from src import utilidades

def gamma(imagen_np: np.ndarray, gamma:float) -> np.ndarray:
    """Aplica la transformación gamma a la imagen."""
    c = (255)**(1-gamma)
    resultado_np = c*(imagen_np**gamma)

    return resultado_np

def umbral(imagen_np: np.ndarray, umbral:int) -> np.ndarray:
    """Convierte la imagen a binaria según un umbral fijo."""
    resultado_np = np.where(imagen_np >= umbral, 255, 0)

    return resultado_np

def negativo(imagen_np: np.ndarray) -> np.ndarray:
    """Invierte los valores de intensidad de la imagen."""
    resultado_np = 255 - imagen_np

    return resultado_np

def ecualizar(imagen_np: np.ndarray) -> np.ndarray:
    """Realiza la ecualización del histograma para mejorar el contraste."""
    imagen_np = imagen_np.astype(np.uint8)
    datos_gris = imagen_np.flatten()

    n_r = np.bincount(datos_gris, minlength=256) # Freq abs(ni)
    NM = datos_gris.size # Pixels totales(n)
    h_r = n_r / NM # Freq relativa(ni/n)

    # Hacemos la suma acumulada
    sk = np.zeros(256)
    for k in range(len(sk)):
        sk[k] = np.sum(h_r[0:k+1])
    
    sk_sombrero = utilidades.escalar_255(sk) # Discretizamos
    resultado_np = sk_sombrero[imagen_np] # Lookup table

    return resultado_np