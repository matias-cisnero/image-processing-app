import numpy as np
from typing import Tuple

def media(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.ones((k, k))

    factor = 1 / np.sum(filtro)
    return (filtro, factor)

def mediana(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.ones((k, k)).astype(int)

    factor = 1
    return (filtro, factor)

def mediana_ponderada(k: int) -> Tuple[np.ndarray, float]:
    filtro_gauss, _ = gaussiana(k)
    filtro = (filtro_gauss * 50).astype(int)

    factor = 1
    return (filtro, factor)

def gaussiana(sigma: int) -> Tuple[np.ndarray, float]:
    k = 2 * sigma + 1
    filtro = np.ones((k, k)).astype(float)
    u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
    #sigma = (k-1) / 2

    for x in range(k):
        for y in range(k):
            filtro[x, y] = (1 / (2 * np.pi * sigma**2)) * np.exp(-((x - u)**2 + (y - u)**2)/(sigma**2))

    factor = 1 / np.sum(filtro)
    return (filtro, factor)

def realce(k: int) -> Tuple[np.ndarray, float]:
    filtro = -1 * np.ones((k, k))
    filtro[k//2, k//2] = k**2 - 1

    factor = 1
    return (filtro, factor)

def prewitt_x(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, -1, -1],
                        [0, 0, 0],
                        [1, 1, 1]])
    
    factor = 1 # usar 1 / 9
    return (filtro, factor)

def prewitt_y(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    
    factor = 1 # usar 1 / 9
    return (filtro, factor)

def sobel_x(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]])
    
    factor = 1
    return (filtro, factor)

def sobel_y(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]])
    
    factor = 1
    return (filtro, factor)

def laplace(k: int) -> Tuple[np.ndarray, float]:
    filtro = np.array([[0, -1, 0],
                        [-1, 4, -1],
                        [0, -1, 0]])
    
    factor = 1
    return (filtro, factor)

def log(sigma: int) -> Tuple[np.ndarray, float]:
    k = 4 * sigma + 1
    filtro = np.ones((k, k)).astype(float)
    u = k // 2 # Centro donde el valor debe ser máximo (son iguales ya que es cuadrada)
    #sigma = (k-1) / 2

    for x in range(k):
        for y in range(k):
            filtro[x, y] = (1 / (2 * np.pi * sigma**3)) * np.exp(-((x - u)**2 + (y - u)**2)/(2 * sigma**2)) * (((x - u)**2 + (y - u)**2)/(sigma**2) - 2)

    factor = 1 #/ np.sum(filtro)
    return (filtro, factor)

def circular_susan() -> np.ndarray:
    filtro = np.array([[0, 0, 1, 1, 1, 0, 0],
                        [0, 1, 1, 1, 1, 1, 0],
                        [1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1],
                        [0, 1, 1, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1, 0, 0]], dtype=int)
    return filtro