import numpy as np
from typing import Tuple
import cv2
from src import operadores

def umbral_iterativo(imagen_np: np.ndarray, n: int = 50) -> np.ndarray:
    T = int(np.mean(imagen_np))
    T_anterior = -1

    for i in range(n):
        if T == T_anterior: break
        T_anterior = T

        imagen_binaria = operadores.umbral(imagen_np, T)
        nG1 = np.sum(imagen_binaria == 255)
        nG2 = np.sum(imagen_binaria == 0)

        m1 = (1 / nG1) * np.sum(imagen_np[imagen_binaria == 255])
        m2 = (1 / nG2) * np.sum(imagen_np[imagen_binaria == 0])

        T = int(0.5 * (m1 + m2))

    print(f"Valor de umbral utilizado(T) = {T} en iteración {i}/{n}")
    resultado_np = operadores.umbral(imagen_np, T)

    return resultado_np

def otsu(imagen_np: np.ndarray) -> np.ndarray:
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
    resultado_np = operadores.umbral(imagen_np, t_estrella)

    return resultado_np

def otsu_rgb(imagen_np: np.ndarray) -> np.ndarray:
    banda_r = imagen_np[:, :, 0]
    banda_g = imagen_np[:, :, 1]
    banda_b = imagen_np[:, :, 2]

    banda_r = otsu(banda_r)
    banda_g = otsu(banda_g)
    banda_b = otsu(banda_b)

    resultado_np = np.dstack([banda_r, banda_g, banda_b])

    # https://numpy.org/doc/stable/reference/generated/numpy.dstack.html
    return resultado_np

# ================================((CONTORNOS ACTIVOS))======================================

def _Fd(θ_0, θ_1, θ_x) -> float:
    return np.log(np.linalg.norm(θ_0 - θ_x, axis=1)/np.linalg.norm(θ_1 - θ_x, axis=1))

def _encontrar_bordes(region1: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
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

def contornos_activos_intercambio_pixeles(imagen_np: np.ndarray, region1: np.ndarray) -> np.ndarray:

    region0 = ~region1

    θ_0 = np.mean(imagen_np[region0], axis=0)
    θ_1 = np.mean(imagen_np[region1], axis=0)

    L_out, L_in = _encontrar_bordes(region1)

    region1_nueva = region1.copy()

    Fd_L_out = _Fd(θ_0, θ_1, imagen_np[L_out])
    region1_nueva[L_out] = Fd_L_out > 0 # Out = False

    Fd_L_in = _Fd(θ_0, θ_1, imagen_np[L_in])
    region1_nueva[L_in] = Fd_L_in > 0 # In = True

    return region1_nueva

def marcar_bordes(imagen_np: np.ndarray, region1: np.ndarray) -> np.ndarray:
    resultado_np = imagen_np.copy()

    L_out, L_in = _encontrar_bordes(region1)

    resultado_np[L_out] = [255, 0, 0]
    
    resultado_np[L_in] = [0, 255, 0]

    return resultado_np

def sift(imagen_np_1: np.ndarray, imagen_np_2: np.ndarray) -> np.ndarray:
    """
    Encuentra y dibuja los puntos de coincidencia (matches) SIFT entre dos imágenes.
    """
    
    # 1. Convertir imágenes NumPy (RGB) a formato OpenCV (BGR)
    img1_bgr = cv2.cvtColor(imagen_np_1, cv2.COLOR_RGB2BGR)
    img2_bgr = cv2.cvtColor(imagen_np_2, cv2.COLOR_RGB2BGR)

    # 2. Convertir a escala de grises (SIFT trabaja sobre grises)
    img1_gray = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2_bgr, cv2.COLOR_BGR2GRAY)

    # 3. Inicializar el detector SIFT
    sift = cv2.SIFT_create()

    # 4. Detectar Keypoints (kp) y Descriptores (des)
    kp1, des1 = sift.detectAndCompute(img1_gray, None)
    kp2, des2 = sift.detectAndCompute(img2_gray, None)

    # 5. Crear el "emparejador" (Matcher)
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    matches = bf.match(des1, des2)

    # 6. Filtrar los "buenos" matches
    U_abs = 100
    good_matches = []
    for m in matches:
        if m.distance < U_abs:
            good_matches.append(m)

    # 7. Dibujar los matches en una nueva imagen
    img_matches_bgr = cv2.drawMatches(
        img1_bgr, kp1,
        img2_bgr, kp2,
        good_matches, 
        None,         
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    
    # 8. Convertir la imagen final de BGR a RGB
    img_matches_rgb = cv2.cvtColor(img_matches_bgr, cv2.COLOR_BGR2RGB)

    # Devuelve el resultado como un np.ndarray (RGB, uint8)
    print(f"Keypoints detectados: {len(kp1)}")
    print(f"Coincidencias buenas: {len(good_matches)}")
    similitud = len(good_matches) / max(len(kp1), 1)
    print(f"'Similitud': {similitud}")
    
    return img_matches_rgb