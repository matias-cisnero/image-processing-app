import numpy as np
from typing import Optional, Tuple

"""
Archivo con la lógica del procesamiento de las imágenes (solo trabaja con arrays de numpy)
"""

# =================================((FUNCIONES_ÚTILES))==================================

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

# ===============================((OPERADORES_PUNTUALES))================================

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

def aplicar_filtro(imagen_np: np.ndarray, func_filtro, k=3, modo=0, mediana=False) -> np.ndarray:
    """
    Convoluciona una máscara con la matriz de la imagen
    
    modo = 0 -> escala el resultado a 255,
    modo = 1 -> clipea el resultado,
    modo = 2 -> no transforma el resultado

    mediana = True -> aplica la mediana
    """
    filtro, factor = func_filtro(k)
    if modo != 2:
        print("Filtro usado:")
        print(filtro)
        print(f"Factor usado: {factor}")
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
        print("Se aplicó un filtro con modo 0 (escalado)")
    elif modo == 1:
        resultado_np = np.clip(imagen_filtrada, 0, 255).astype(np.uint8)
        print("Se aplicó un filtro con modo 1 (clipeado)")
    elif modo == 2:
        resultado_np = imagen_filtrada
        print("Se aplicó un filtro con modo 2 (np.array)")

    return resultado_np

def aplicar_magnitud_del_gradiente(imagen_np: np.ndarray, func_filtro1, func_filtro2) -> np.ndarray:
    """
    Calcula Ix e Iy y realiza la raiz de la suma de sus cuadrados.
    """
    ix = aplicar_filtro(imagen_np, func_filtro=func_filtro1, modo=2)
    iy= aplicar_filtro(imagen_np, func_filtro=func_filtro2, modo=2)

    magnitud = np.sqrt((ix**2)+(iy**2))

    resultado_np = escalar_255(magnitud)

    return resultado_np

# ============================((MÉTODO DEL LAPLACIANO))==================================

def crear_filtro_laplace(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[0, -1, 0],
                        [-1, 4, -1],
                        [0, -1, 0]])
    factor = 1
    return (filtro, factor)

def crear_filtro_log(sigma: int) -> Tuple[np.ndarray, float]:
    k = 4 * sigma + 1
    filtro = np.ones((k, k)).astype(float)
    u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
    #sigma = (k-1) / 2

    for x in range(k):
        for y in range(k):
            filtro[x, y] = (1 / (2 * np.pi * sigma**3)) * np.exp(-((x - u)**2 + (y - u)**2)/(2 * sigma**2)) * (((x - u)**2 + (y - u)**2)/(sigma**2) - 2)

    factor = 1 #/ np.sum(filtro)
    #print(f"Factor usado: {1} / {np.sum(filtro)}")
    return (filtro, factor)

def encontrar_cruces_por_cero(imagen_np: np.ndarray) -> np.ndarray:
    m, n, _ = imagen_np.shape
    imagen_filtrada = np.zeros_like(imagen_np) # Predeterminadamente son cero y solo cambio los 255

    for i in range(m):
        for j in range(n - 1):
            for c in range(3):
                if imagen_np[i, j, c] * imagen_np[i, j + 1, c] < 0:
                    imagen_filtrada[i, j] = 255

    return imagen_filtrada # Retorna una img binaria

def encontrar_cruces_por_cero_vectorizado(imagen_np: np.ndarray) -> np.ndarray:
    imagen_filtrada = np.zeros_like(imagen_np)

    mascara = (imagen_np[:, :-1] * imagen_np[:, 1:]) < 0

    imagen_filtrada[:, :-1][mascara] = 255

    return imagen_filtrada

def encontrar_cruces_por_cero_pendiente(imagen_np: np.ndarray, umbral=128) -> np.ndarray:
    m, n, _ = imagen_np.shape
    imagen_filtrada = np.zeros_like(imagen_np) # Predeterminadamente son cero y solo cambio los 255

    for i in range(m):
        for j in range(n - 1):
            for c in range(3):
                if abs(imagen_np[i, j, c]) + abs(imagen_np[i, j + 1, c]) > umbral:
                    imagen_filtrada[i, j] = 255

    return imagen_filtrada # Retorna una img binaria

def encontrar_cruces_por_cero_pendiente_vectorizado(imagen_np: np.ndarray, umbral=128) -> np.ndarray:
    imagen_filtrada = np.zeros_like(imagen_np)

    mascara = (np.abs(imagen_np[:, :-1]) + np.abs(imagen_np[:, 1:])) > umbral

    imagen_filtrada[:, :-1][mascara] = 255

    return imagen_filtrada

def aplicar_metodo_del_laplaciano(imagen_np: np.ndarray, log: bool = False, pendiente: bool = False, umbral: int = 50, sigma: int = 1) -> np.ndarray:
    if not log:
        img = aplicar_filtro(imagen_np, func_filtro=crear_filtro_laplace, modo=2)
    else:
        img = aplicar_filtro(imagen_np, func_filtro=crear_filtro_log, k=sigma, modo=2)
    if not pendiente:
        img = encontrar_cruces_por_cero(img)
    else:
        img = encontrar_cruces_por_cero_pendiente(img, umbral=umbral)
    return img

# ==============================((FILTRO DE DIFUSIÓN))===================================

# --- Detectores de borde ---

def detector_de_leclerc(gradiente, sigma:int):
    return np.exp((-(gradiente**2))/sigma**2)

def detector_de_lorentz(gradiente, sigma:int):
    return 1/(((-(gradiente**2))/sigma**2) + 1)

# --- Difusión ---

def aplicar_filtro_difusion(imagen_np: np.ndarray, t: float, sigma: int, isotropico: bool = False, lamb: float = 0.25) -> np.ndarray:
    m, n, _ = imagen_np.shape
    imagen_filtrada = imagen_np.copy()

    for _ in range(t):
        for i in range(1, m - 1):
            for j in range(1, n - 1):
                for c in range(3):

                    # Gradientes
                    DN = imagen_filtrada[i, j + 1, c] - imagen_filtrada[i, j, c]
                    DE = imagen_filtrada[i - 1, j, c] - imagen_filtrada[i, j, c]
                    DO = imagen_filtrada[i + 1, j, c] - imagen_filtrada[i, j, c]
                    DS = imagen_filtrada[i, j - 1, c] - imagen_filtrada[i, j, c]
                    
                    # Coeficientes
                    if isotropico:
                        cN = cE = cO = cS = 1
                    else:
                        cN = detector_de_leclerc(DN, sigma)
                        cE = detector_de_leclerc(DE, sigma)
                        cO = detector_de_leclerc(DO, sigma)
                        cS = detector_de_leclerc(DS, sigma)

                    # Actualización
                    imagen_filtrada[i, j, c] += lamb * (DN * cN + DE * cE + DO * cO + DS * cS)
    
    resultado_np = escalar_255(imagen_filtrada)
    return resultado_np

# ===============================((FILTRO BILATERAL))====================================

def aplicar_filtro_bilateral(imagen_np: np.ndarray, sigma_s: int = 1, sigma_r: int = 1) -> np.ndarray:

    Gs, factor = crear_filtro_gaussiano(sigma_s)
    print("Filtro espacial usado:")
    print(Gs)
    m, n, _ = imagen_np.shape
    k, l = Gs.shape
    pad_h, pad_w = k//2, l//2

    # Padding e imagen filtrada
    imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
    imagen_filtrada = np.zeros_like(imagen_np)

    for i in range(m):
        for j in range(n):
            region = imagen_padded[i:i+k, j:j+l, :]

            dif = region - region[pad_h, pad_w, :]
            #print(f"Shape de dif: {dif.shape}")
            Gr = np.exp(-(np.sum(dif**2, axis=2) / (2 * sigma_r**2)))
            #print(f"Shape de Gr: {Gr.shape}")

            Wx = np.sum(Gs * Gr)

            G = Gs * Gr
            G = G[:, :, np.newaxis]

            valor = (1 / Wx) * np.sum(region * G, axis=(0, 1))
            #print(f"Shape de valor: {valor.shape}")
            
            imagen_filtrada[i, j, :] = valor
    
    resultado_np = escalar_255(imagen_filtrada)
    return resultado_np

# ================================((UMBRALIZACIÓN))======================================

# --- Cálculo iterativo del umbral (escala de grises) ---

def aplicar_umbralizacion_iterativa(imagen_np: np.ndarray, n: int = 50) -> np.ndarray:
    T = int(np.mean(imagen_np))
    T_anterior = -1

    for i in range(n):
        if T == T_anterior: break
        T_anterior = T

        imagen_binaria = aplicar_umbralizacion(imagen_np, T)
        nG1 = np.sum(imagen_binaria == 255)
        nG2 = np.sum(imagen_binaria == 0)

        m1 = (1 / nG1) * np.sum(imagen_np[imagen_binaria == 255])
        m2 = (1 / nG2) * np.sum(imagen_np[imagen_binaria == 0])

        T = int(0.5 * (m1 + m2))

    print(f"Valor de umbral utilizado(T) = {T} en iteración {i}/{n}")
    resultado_np = aplicar_umbralizacion(imagen_np, T)

    return resultado_np

def aplicar_umbralizacion_de_otsu(imagen_np: np.ndarray) -> np.ndarray:
    imagen_np = imagen_np.astype(np.uint8)
    datos_gris = imagen_np.flatten()

    intensidad = np.arange(256)
    fi = np.bincount(datos_gris, minlength=256) 
    N = datos_gris.size
    pi = fi / N

    # Computar las sumas acumuladas (array) y promedios ponderados (array)
    P1 = np.zeros(256)
    m = np.zeros(256)
    for t in range(256):
        P1[t] = np.sum(pi[0:t+1])
        m[t] = np.sum(intensidad[0:t+1] * pi[0:t+1])
    
    # Computar el promedio ponderado global (escalar)
    mG = m[255] # np.sum(intensidad * pi)

    # Computar la varianza entre clases
    sigma_B = np.zeros(256)
    for t in range(256):
        if P1[t] > 0 and P1[t] < 1:
            sigma_B[t] = ((mG * P1[t] - m[t])**2) / (P1[t] * (1 - P1[t]))

    t_estrella = np.argmax(sigma_B)

    print(f"Valor de umbral utilizado(T) = {t_estrella}")
    resultado_np = aplicar_umbralizacion(imagen_np, t_estrella)

    return resultado_np

def aplicar_umbralizacion_rgb(imagen_np: np.ndarray) -> np.ndarray:
    banda_r = imagen_np[:, :, 0]
    banda_g = imagen_np[:, :, 1]
    banda_b = imagen_np[:, :, 2]

    banda_r = aplicar_umbralizacion_de_otsu(banda_r)
    banda_g = aplicar_umbralizacion_de_otsu(banda_g)
    banda_b = aplicar_umbralizacion_de_otsu(banda_b)

    resultado_np = np.dstack([banda_r, banda_g, banda_b])

    # https://numpy.org/doc/stable/reference/generated/numpy.dstack.html
    return resultado_np

# ================================((DETECTORES DE BORDE AVANZADOS))======================================

def discretizar_angulos(phi_grados: np.ndarray) -> np.ndarray:
    angulo = np.zeros_like(phi_grados)

    mask = (phi_grados <= 22.5) | (phi_grados > 157.5) # Zona amarilla
    angulo[mask] = 0
    mask = (phi_grados > 22.5) & (phi_grados <= 67.5) # Zona verde
    angulo[mask] = 45
    mask = (phi_grados > 67.5) & (phi_grados <= 112.5) # Zona azul
    angulo[mask] = 90
    mask = (phi_grados > 112.5) & (phi_grados <= 157.5) # Zona roja
    angulo[mask] = 135

    return angulo

def obtener_vecinos(magnitud: np.ndarray, i: int, j: int, angulo: float) -> np.ndarray:
    if angulo == 0:
        return [magnitud[i-1, j], magnitud[i+1, j]]
    elif angulo == 45:
        return [magnitud[i-1, j-1], magnitud[i+1, j+1]]
    elif angulo == 90:
        return [magnitud[i, j-1], magnitud[i, j+1]]
    elif angulo == 135:
        return [magnitud[i-1, j+1], magnitud[i+1, j-1]]
    else:
        return []

def aplicar_umbralizacion_histeresis(magnitud: np.ndarray, t1: int, t2: int) -> np.ndarray:
    m, n = magnitud.shape
    pad = 1

    magnitud_padded = np.pad(magnitud, ((pad, pad), (pad, pad)), mode='constant')

    for i in range(m):
        for j in range(n):

            region = magnitud_padded[i:i+2*pad+1, j:j+2*pad+1]

            centro = region[pad, pad]

            if centro > t2:
                magnitud[i, j] = 255
            elif centro < t1:
                magnitud[i, j] = 0
            else:
                if np.any(region > t2):
                    magnitud[i, j] = 255
                else:
                    magnitud[i, j] = 0
    return magnitud

def aplicar_umbralizacion_histeresis2(imagen_np: np.ndarray, t1: int, t2: int) -> np.ndarray:
    m, n = imagen_np.shape
    
    # Clasificar píxeles: 255 (Fuerte), 128 (Débil), 0 (No-Borde)
    bordes = np.zeros((m, n), dtype=np.uint8)
    bordes[imagen_np > t2] = 255
    bordes[(imagen_np >= t1) & (imagen_np <= t2)] = 128

    # Bucle de propagación
    while True:
        pixeles_promovidos = 0
        
        for i in range(1, m - 1):
            for j in range(1, n - 1):
                if bordes[i, j] == 128: # Si es un píxel débil
                    vecindad = bordes[i-1 : i+2, j-1 : j+2]
                    if np.any(vecindad == 255): # Si toca a un píxel fuerte
                        bordes[i, j] = 255
                        pixeles_promovidos += 1
                        
        if pixeles_promovidos == 0:
            break

    # Limpieza final: elimina los débiles que no se conectaron
    bordes[bordes == 128] = 0
    return bordes

def aplicar_detector_canny(imagen_np: np.ndarray, t1: int, t2: int) -> np.ndarray:

    imagen_np = np.stack([imagen_np, imagen_np, imagen_np], axis=-1) # para tener los 3 canales
    # 1) aplico filtro gaussiano
    #imagen_np = aplicar_filtro(imagen_np, func_filtro=crear_filtro_gaussiano, modo=0)

    # 2) aplico sobel y calculo la magnitud
    ix = aplicar_filtro(imagen_np, func_filtro=crear_filtro_sobel_x, modo=2)[:, :, 0]
    iy= aplicar_filtro(imagen_np, func_filtro=crear_filtro_sobel_y, modo=2)[:, :, 0]
    magnitud = np.sqrt((ix**2)+(iy**2))

    # 3) calculo el angulo del gradiente
    phi = np.arctan2(iy, ix) # ángulos en [-π, π] -> https://numpy.org/doc/stable/reference/generated/numpy.arctan2.html
    phi[phi < 0] += np.pi # convertimos negativos a [0, π]
    phi_grados = np.degrees(phi)  # convierte a grados: 0 a 180

    # 4) se discretizan los angulos
    angulo = discretizar_angulos(phi_grados)
    print(f"angulo calculado correctamente")

    # 5) supresión de no máximos
    m, n = magnitud.shape
    magnitud_snm = magnitud.copy()

    for i in range(1, m-1):
        for j in range(1, n-1):
            if magnitud_snm[i, j] == 0:
                continue
            vecinos = obtener_vecinos(magnitud, i, j, angulo[i, j])
            if magnitud_snm[i, j] < max(vecinos):
                magnitud_snm[i, j] = 0

    # 6) aplico umbralización por histéresis
    resultado_np = aplicar_umbralizacion_histeresis2(magnitud_snm, t1, t2)
    resultado_np = np.stack([resultado_np, resultado_np, resultado_np], axis=-1)

    return resultado_np

def crear_mascara_circular() -> np.ndarray:
    mascara = np.array([[0, 0, 1, 1, 1, 0, 0],
                        [0, 1, 1, 1, 1, 1, 0],
                        [1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1],
                        [0, 1, 1, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1, 0, 0]], dtype=int)
    return mascara

def aplicar_metodo_susan(imagen_np: np.ndarray, modo: str) -> np.ndarray:
    t = 15
    filtro = crear_mascara_circular()

    m, n, _ = imagen_np.shape
    k, l = filtro.shape
    pad_h, pad_w = k//2, l//2

    # Padding e imagen filtrada
    imagen_padded = np.pad(imagen_np, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
    imagen_filtrada = np.zeros_like(imagen_np)

    for i in range(m):
        for j in range(n):
            region = imagen_padded[i:i+k, j:j+l, :]
            region_circular = region[filtro == 1]
            centro = region[pad_h, pad_w, :]

            dif = np.linalg.norm(region_circular - centro, axis=1)
            c_r0 = (dif < t).astype(int)

            n_r0 = np.sum(c_r0)
            s_r0 = 1 - (n_r0 / 37)

            if s_r0 < 0.35:
                continue  # no borde
            elif s_r0 > 0.35 and modo == "borde":
                imagen_filtrada[i, j, 2] = 255  # borde color azul
            elif s_r0 > 0.60 and modo == "esquina":
                imagen_filtrada[i, j, 0] = 255  # esquina color rojo

    bordes = np.any(imagen_filtrada != 0, axis=-1)
    resultado_np = imagen_np.copy()
    resultado_np[bordes] = imagen_filtrada[bordes]

    return resultado_np

from PIL import Image, ImageDraw

def aplicar_transformada_de_hough(imagen_np: np.ndarray, umbral: int = 100) -> np.ndarray:

    imagen_np = np.stack([imagen_np, imagen_np, imagen_np], axis=-1) 

    #1 Hallar los bordes de la imagen utilizando un método de detección de bordes.
    magnitud = aplicar_magnitud_del_gradiente(imagen_np, crear_filtro_sobel_x, crear_filtro_sobel_y)

    #2 Umbralizar para obtener una imagen binaria.
    magnitud = aplicar_umbralizacion_de_otsu(magnitud)
    magnitud = magnitud[:, :, 0]
    
    #3 Subdividir el plano (r, θ) discretizando en una cantidad específica de puntos.
    m, n = magnitud.shape
    diagonal = int(np.round(np.sqrt(m**2 + n**2)))
    r = np.arange(-diagonal, diagonal)

    θ = np.linspace(-np.pi/2, np.pi/2, 180) # valores entre +-90
    cos_θ = np.cos(θ)
    sin_θ = np.sin(θ)
    
    A = np.zeros((len(r), len(θ)), dtype=np.int32)
    
    #4 Para cada pixel blanco de la imagen, decidir si cumple la ecuación normal de la recta, en caso afirmativo aumentar el acumulador.
    ϵ = 2
    y, x = np.where(magnitud == 255)

    # x e (P, 1), cos_θ e (1, θ) => x * cos_θ e (P, θ)
    prod = x[:, None] * cos_θ[None, :] + y[:, None] * sin_θ[None, :]   # (P, θ)
    print(f"Shape de prod: {prod.shape}, p={len(x)}, θ={len(θ)}, r={len(r)}")

    # resta e (P, θ, 1), r e (1, 1, R) => resta * r e (P, θ, R)
    for i, r_i in enumerate(r):
        dif = np.abs(r_i - prod)
        A[i, :] = np.sum(dif < ϵ, axis=0)

    #5 Examinar el contenido de las celdas del acumulador con altas concentraciones (tomar el máximo o umbralizar).
    maximos = np.argwhere(A >= umbral)
    print(f"Lineas encontradas: {maximos.shape[0]}")

    #6 Graficar las rectas encontradas.
    img_pil = Image.fromarray(np.uint8(imagen_np))
    draw = ImageDraw.Draw(img_pil)

    for i_r, i_θ in maximos:
        r_val = r[i_r]
        θ_val = θ[i_θ]
        
        a = np.cos(θ_val)
        b = np.sin(θ_val)
        x0 = a * r_val
        y0 = b * r_val

        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        
        draw.line([(x1, y1), (x2, y2)], fill=(255, 0, 0), width=1)
    
    resultado_np = np.array(img_pil)
    return resultado_np

# ================================((CONTORNOS ACTIVOS))======================================

def Fd(θ_0, θ_1, θ_x) -> float:
    return np.log(np.linalg.norm(θ_0 - θ_x, axis=1)/np.linalg.norm(θ_1 - θ_x, axis=1))

def encontrar_bordes(region1: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Devuelve L_out (borde externo) y L_in (borde interno) de una región binaria.
    region1 debe ser una máscara booleana (True = objeto, False = fondo).
    """
    
    # Dilatación (para borde externo)
    dilatacion = (
        region1 |
        np.roll(region1, 1, axis=0) | np.roll(region1, -1, axis=0) |
        np.roll(region1, 1, axis=1) | np.roll(region1, -1, axis=1) |
        np.roll(np.roll(region1, 1, axis=0), 1, axis=1) |
        np.roll(np.roll(region1, 1, axis=0), -1, axis=1) |
        np.roll(np.roll(region1, -1, axis=0), 1, axis=1) |
        np.roll(np.roll(region1, -1, axis=0), -1, axis=1)
    )
    L_out = np.logical_and(~region1, dilatacion)

    # Erosión (para borde interno)
    erosion = (
        region1 &
        np.roll(region1, 1, axis=0) & np.roll(region1, -1, axis=0) &
        np.roll(region1, 1, axis=1) & np.roll(region1, -1, axis=1) &
        np.roll(np.roll(region1, 1, axis=0), 1, axis=1) &
        np.roll(np.roll(region1, 1, axis=0), -1, axis=1) &
        np.roll(np.roll(region1, -1, axis=0), 1, axis=1) &
        np.roll(np.roll(region1, -1, axis=0), -1, axis=1)
    )
    L_in = np.logical_and(region1, ~erosion)

    # Limpieza de bordes
    L_out[[0, -1], :] = L_out[:, [0, -1]] = False
    L_in[[0, -1], :] = L_in[:, [0, -1]] = False

    return L_out, L_in

def obtener_segmentacion_cn_ip(imagen_np: np.ndarray, region1: np.ndarray) -> np.ndarray:

    region0 = ~region1

    θ_0 = np.mean(imagen_np[region0], axis=0)
    θ_1 = np.mean(imagen_np[region1], axis=0)

    L_out, L_in = encontrar_bordes(region1)

    region1_nueva = region1.copy()

    Fd_L_out = Fd(θ_0, θ_1, imagen_np[L_out])
    region1_nueva[L_out] = Fd_L_out > 0 # Out = False

    Fd_L_in = Fd(θ_0, θ_1, imagen_np[L_in])
    region1_nueva[L_in] = Fd_L_in > 0 # In = True

    return region1_nueva

def marcar_borde(imagen_np: np.ndarray, region1: np.ndarray) -> np.ndarray:
    resultado_np = imagen_np.copy()

    L_out, L_in = encontrar_bordes(region1)

    resultado_np[L_out] = [255, 0, 0]
    
    resultado_np[L_in] = [0, 255, 0]

    return resultado_np
