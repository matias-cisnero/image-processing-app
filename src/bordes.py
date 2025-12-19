import numpy as np
from PIL import Image, ImageDraw
from src import transformaciones, mascaras, filtros, segmentaciones

def magnitud_gradiente(imagen_np: np.ndarray, func_filtro1, func_filtro2) -> np.ndarray:
    """
    Calcula Ix e Iy y realiza la raiz de la suma de sus cuadrados.
    """
    ix = filtros.convolucionar(imagen_np, func_filtro=func_filtro1, modo=2)
    iy= filtros.convolucionar(imagen_np, func_filtro=func_filtro2, modo=2)

    magnitud = np.sqrt((ix**2)+(iy**2))

    resultado_np = transformaciones.escalar_255(magnitud)

    return resultado_np

def _cruces_por_cero(imagen_np: np.ndarray) -> np.ndarray:
    m, n, _ = imagen_np.shape
    imagen_filtrada = np.zeros_like(imagen_np) # Predeterminadamente son cero y solo cambio los 255

    for i in range(m):
        for j in range(n - 1):
            for c in range(3):
                if imagen_np[i, j, c] * imagen_np[i, j + 1, c] < 0:
                    imagen_filtrada[i, j] = 255

    return imagen_filtrada # Retorna una img binaria

def _cruces_por_cero_pendiente(imagen_np: np.ndarray, umbral=128) -> np.ndarray:
    m, n, _ = imagen_np.shape
    imagen_filtrada = np.zeros_like(imagen_np) # Predeterminadamente son cero y solo cambio los 255

    for i in range(m):
        for j in range(n - 1):
            for c in range(3):
                if abs(imagen_np[i, j, c]) + abs(imagen_np[i, j + 1, c]) > umbral:
                    imagen_filtrada[i, j] = 255

    return imagen_filtrada # Retorna una img binaria

def laplaciano(imagen_np: np.ndarray, log: bool = False, pendiente: bool = False, umbral: int = 50, sigma: int = 1) -> np.ndarray:
    if not log:
        img = filtros.convolucionar(imagen_np, func_filtro=mascaras.laplace, modo=2)
    else:
        img = filtros.convolucionar(imagen_np, func_filtro=mascaras.log, k=sigma, modo=2)
    if not pendiente:
        img = _cruces_por_cero(img)
    else:
        img = _cruces_por_cero_pendiente(img, umbral=umbral)
    return img

# ================================((DETECTORES DE BORDE AVANZADOS))======================================

def _discretizar_angulos(phi_grados: np.ndarray) -> np.ndarray:
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

def _obtener_vecinos_canny(magnitud: np.ndarray, i: int, j: int, angulo: float) -> np.ndarray:
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

def _histeresis(magnitud: np.ndarray, t1: int, t2: int) -> np.ndarray:
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

def _histeresis2(imagen_np: np.ndarray, t1: int, t2: int) -> np.ndarray:
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

def canny(imagen_np: np.ndarray, t1: int, t2: int) -> np.ndarray:

    imagen_np = np.stack([imagen_np, imagen_np, imagen_np], axis=-1) # para tener los 3 canales
    # 1) aplico filtro gaussiano
    #imagen_np = aplicar_filtro(imagen_np, func_filtro=crear_filtro_gaussiano, modo=0)

    # 2) aplico sobel y calculo la magnitud
    ix = filtros.convolucionar(imagen_np, func_filtro=mascaras.sobel_x, modo=2)[:, :, 0]
    iy= filtros.convolucionar(imagen_np, func_filtro=mascaras.sobel_y, modo=2)[:, :, 0]
    magnitud = np.sqrt((ix**2)+(iy**2))

    # 3) calculo el angulo del gradiente
    phi = np.arctan2(iy, ix) # ángulos en [-π, π] -> https://numpy.org/doc/stable/reference/generated/numpy.arctan2.html
    phi[phi < 0] += np.pi # convertimos negativos a [0, π]
    phi_grados = np.degrees(phi)  # convierte a grados: 0 a 180

    # 4) se discretizan los angulos
    angulo = _discretizar_angulos(phi_grados)
    print(f"angulo calculado correctamente")

    # 5) supresión de no máximos
    m, n = magnitud.shape
    magnitud_snm = magnitud.copy()

    for i in range(1, m-1):
        for j in range(1, n-1):
            if magnitud_snm[i, j] == 0:
                continue
            vecinos = _obtener_vecinos_canny(magnitud, i, j, angulo[i, j])
            if magnitud_snm[i, j] < max(vecinos):
                magnitud_snm[i, j] = 0

    # 6) aplico umbralización por histéresis
    resultado_np = _histeresis2(magnitud_snm, t1, t2)
    resultado_np = np.stack([resultado_np, resultado_np, resultado_np], axis=-1)

    return resultado_np

def susan(imagen_np: np.ndarray, modo: str) -> np.ndarray:
    t = 15
    filtro = mascaras.circular_susan()

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

def _dibujar_rectas(imagen_np: np.ndarray, maximos: np.ndarray, r: np.ndarray, θ: np.ndarray) -> np.ndarray:
    img_pil = Image.fromarray(np.uint8(imagen_np))
    draw = ImageDraw.Draw(img_pil)

    for i_r, i_θ in maximos:
        r_val = r[i_r]
        θ_val = θ[i_θ]
        
        a = np.cos(θ_val)
        b = np.sin(θ_val)
        x0 = a * r_val
        y0 = b * r_val

        # Dibujar línea larga atravesando toda la imagen
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        
        draw.line([(x1, y1), (x2, y2)], fill=(255, 0, 0), width=1)

    return np.array(img_pil)

def transformada_de_hough(imagen_np: np.ndarray, umbral: int = 100) -> np.ndarray:

    imagen_np = np.stack([imagen_np, imagen_np, imagen_np], axis=-1) 

    #1 Hallar los bordes de la imagen utilizando un método de detección de bordes.
    magnitud = magnitud_gradiente(imagen_np, mascaras.sobel_x, mascaras.sobel_y)

    #2 Umbralizar para obtener una imagen binaria.
    magnitud = segmentaciones.otsu(magnitud)
    magnitud = magnitud[:, :, 0]
    
    #3 Subdividir el plano (r, θ) discretizando en una cantidad específica de puntos.
    m, n = magnitud.shape
    diagonal = int(np.round(np.sqrt(m**2 + n**2)))
    r = np.arange(-diagonal, diagonal)

    θ = np.linspace(-np.pi/2, np.pi/2, 180) # valores entre +-90
    cos_θ = np.cos(θ)
    sin_θ = np.sin(θ)
    
    #4 Para cada pixel blanco de la imagen, decidir si cumple la ecuación normal de la recta, en caso afirmativo aumentar el acumulador.
    A = np.zeros((len(r), len(θ)), dtype=np.int32)
    ϵ = 2
    y, x = np.where(magnitud == 255)

    prod = x[:, None] * cos_θ[None, :] + y[:, None] * sin_θ[None, :]   # (P, θ)
    #print(f"Shape de prod: {prod.shape}, p={len(x)}, θ={len(θ)}, r={len(r)}")

    for i, r_i in enumerate(r):
        dif = np.abs(r_i - prod)
        A[i, :] = np.sum(dif < ϵ, axis=0)

    #5 Examinar el contenido de las celdas del acumulador con altas concentraciones (tomar el máximo o umbralizar).
    maximos = np.argwhere(A >= umbral)
    print(f"Lineas encontradas: {maximos.shape[0]}")

    #6 Graficar las rectas encontradas.
    resultado_np = _dibujar_rectas(imagen_np, maximos, r, θ)

    return resultado_np