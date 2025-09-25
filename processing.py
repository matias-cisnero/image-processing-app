import numpy as np
from typing import Optional, Tuple, Callable

"""
Archivo con la lógica del procesamiento de las imágenes (solo trabaja con arrays de numpy)
"""

# ===============================((FUNCIONES_AUXILIARES))================================

def detector_de_leclerc(gradiente: np.ndarray, sigma:int) -> np.ndarray:
    return np.exp((-(gradiente**2))/sigma**2)

def detector_de_lorentz(gradiente: np.ndarray, sigma:int) -> np.ndarray:
    return 1/(((-(gradiente**2))/sigma**2) + 1)

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

# ================================((HISTOGRAMAS))========================================

def aplicar_ecualizacion_histograma(imagen_np: np.ndarray) -> np.ndarray:
    """
    Realiza la ecualización del histograma.
    """
    imagen_np = imagen_np.astype(np.uint8)
    datos_gris = imagen_np.flatten()

    n_r = np.bincount(datos_gris, minlength=256) # Freq abs(ni)
    NM = datos_gris.size # Pixels totales(n)
    h_r = n_r / NM # Freq relativa(ni/n)

    # Hacemos la suma acumulada
    sk = np.zeros(256)
    for k in range(len(sk)):
        sk[k] = np.sum(h_r[0:k+1])
    
    sk_sombrero = escalar_255(sk) # Discretizamos
    resultado_np = sk_sombrero[imagen_np] # Lookup table

    return resultado_np

# ===================================((RUIDO))===========================================

# --- Generar Vector Ruido (Gaussiano, Rayleigh, Exponencial)

def generar_vector_ruido(distribucion, intensidad, cantidad) -> np.ndarray:
    # distribucion = np.random.normal, np.random.rayleigh, np.random.exponential
    vector_aleatorio = distribucion(scale=intensidad, size=(cantidad, 1))

    return vector_aleatorio

# -- Aditivo y Multiplicativo

def aplicar_ruido(imagen_np: np.ndarray, tipo: str, vector_ruido: np.ndarray, d: int) -> np.ndarray:
    """
    Aplica un vector de ruido a una imagen de forma aditiva o multiplicativa.
    """
    #print("jeje, si anda el ruido")
    m, n, _ = imagen_np.shape # Esto es para quedarme con 256 x 256 e ignorar los 3 canales rgb

    # Cantidad de píxeles contaminados
    num_contaminados = int((d * (m * n)) / 100)
    # num_contaminados = len(vector_ruido)
    D = np.unravel_index(np.random.choice(m * n, num_contaminados, replace=False),(m, n))

    # Generar la imagen contaminada I_c
    if tipo == "Aditivo": imagen_np[D] += vector_ruido
    elif tipo == "Multiplicativo": imagen_np[D] *= vector_ruido
    
    resultado_np = escalar_255(imagen_np)
    
    return resultado_np

# --- Sal y Pimienta

def aplicar_ruido_sal_y_pimienta(imagen_np: np.ndarray, p: int) -> np.ndarray:

    m, n, _ = imagen_np.shape

    for i in range(m):
        for j in range(n):
            x = np.random.rand()
            if x <= p:
                imagen_np[i, j, :] = 0 # pimienta (negro)
            elif x > (1-p):
                imagen_np[i, j, :] = 255 # sal (blanco)

    return imagen_np


# ===================================((FILTROS))=========================================

# --- Media

def crear_filtro_media(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.ones((k, k))

    factor = 1 / np.sum(filtro)
    return (filtro, factor)

# --- Mediana
def crear_filtro_mediana(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.ones((k, k)).astype(int)
    factor = 1
    return (filtro, factor)

# --- Mediana Ponderada

def crear_filtro_mediana_ponderada(k: int) -> Tuple[np.ndarray, float]:
    filtro_gauss, _ = crear_filtro_gaussiano(k)
    filtro = (filtro_gauss * 50).astype(int)

    factor = 1
    return (filtro, factor)

# --- Gaussiano

def crear_filtro_gaussiano(sigma: int) -> Tuple[np.ndarray, float]:
    k = 2 * sigma + 1
    filtro = np.ones((k, k)).astype(float)
    u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
    #sigma = (k-1) / 2

    for x in range(k):
        for y in range(k):
            filtro[x, y] = (1 / (2 * np.pi * sigma**2)) * np.exp(-((x - u)**2 + (y - u)**2)/(sigma**2))

    factor = 1 / np.sum(filtro)
    #print(f"Factor usado: {1} / {np.sum(filtro)}")
    return (filtro, factor)

# --- Realce de Bordes

def crear_filtro_realce(k: int) -> Tuple[np.ndarray, float]:
    filtro = -1 * np.ones((k, k))
    filtro[k//2, k//2] = k**2 - 1

    factor = 1
    return (filtro, factor)

# --- Realce de Bordes Prewitt

def crear_filtro_prewitt_x(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, -1, -1],
                        [0, 0, 0],
                        [1, 1, 1]])
    factor = 1 # usar 1 / 9
    return (filtro, factor)

def crear_filtro_prewitt_y(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    factor = 1 # usar 1 / 9
    return (filtro, factor)

# --- Realce de Bordes Sobel

def crear_filtro_sobel_x(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]])
    factor = 1
    return (filtro, factor)

def crear_filtro_sobel_y(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]])
    factor = 1
    return (filtro, factor)

# --- Máscara de Laplace

def crear_filtro_laplace(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[0, -1, 0],
                        [-1, 4, -1],
                        [0, -1, 0]])
    factor = 1
    return (filtro, factor)

def aplicar_filtro(imagen_np: np.ndarray, func_filtro, k=3, modo=0, mediana=False) -> np.ndarray:
    """
    Convoluciona una máscara con la matriz de la imagen
    
    modo = 0 -> escala el resultado a 255,
    modo = 1 -> clipea el resultado,
    modo = 2 -> no transforma el resultado

    mediana = True -> aplica la mediana
    """
    filtro, factor = func_filtro(k)
    print("Filtro usado:")
    print(filtro)
    print("Factor usado:")
    print(factor)
    m, n, _ = imagen_np.shape
    k, l = filtro.shape
    pad_h, pad_w = k//2, l//2

    # Padding e imagen filtrada
    imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
    imagen_filtrada = np.zeros_like(imagen_np)

    indices_repeticion = filtro.flatten().astype(int) # Solo para mediana

    # Bucle para filtrado (c para los canales)
    for i in range(m):
        for j in range(n):
            for c in range(3):
                region = imagen_padded[i:i+k, j:j+l, c]
                if not mediana:
                    valor = np.sum(region * filtro) * factor
                else:
                    valores = np.repeat(region.flatten(), indices_repeticion) # Indica cuantas veces se repite cada indice
                    valor = np.median(valores) # Mediana
                imagen_filtrada[i, j, c] = valor

    if modo == 0:
        resultado_np = escalar_255(imagen_filtrada)
        print("modo 0")
    elif modo == 1:
        resultado_np = np.clip(imagen_filtrada, 0, 255).astype(np.uint8)
        print("modo 1")
    elif modo == 2:
        resultado_np = imagen_filtrada
        print("modo 2")

    return resultado_np

def aplicar_filtro_combinado(imagen_np: np.ndarray, func_filtro1, func_filtro2) -> np.ndarray:
    """
    Aplica dos filtros (x e y) y combina sus resultados.
    """
    img1 = aplicar_filtro(imagen_np, func_filtro=func_filtro1, modo=2)
    img2 = aplicar_filtro(imagen_np, func_filtro=func_filtro2, modo=2)

    imagen_filtrada = np.sqrt((img1**2)+(img2**2))

    resultado_np = escalar_255(imagen_filtrada)

    return resultado_np

def aplicar_filtro_isotropico(imagen_np: np.ndarray, t: float) -> np.ndarray:
    for i in range(t):
        imagen_np = aplicar_filtro(imagen_np, func_filtro=crear_filtro_gaussiano, k=t, modo=2)
    
    resultado_np = escalar_255(imagen_np)

    return resultado_np