import numpy as np
from src import utilidades

def generar_vector(distribucion, intensidad, cantidad) -> np.ndarray:
    """
    Genera valores aleatorios basados en una distribución (np.random.normal, etc).
    """
    vector_aleatorio = distribucion(scale=intensidad, size=(cantidad, 1))

    return vector_aleatorio

def aplicar(imagen_np: np.ndarray, tipo: str, vector_ruido: np.ndarray, d: int) -> np.ndarray:
    """
    Aplica ruido de forma aditiva o multiplicativa a una densidad porcentual de píxeles.
    """
    m, n, _ = imagen_np.shape # Esto es para quedarme con 256 x 256 e ignorar los 3 canales rgb

    # Cantidad de píxeles contaminados
    num_contaminados = int((d * (m * n)) / 100)
    # num_contaminados = len(vector_ruido)
    D = np.unravel_index(np.random.choice(m * n, num_contaminados, replace=False),(m, n))

    # Generar la imagen contaminada I_c
    if tipo == "Aditivo": imagen_np[D] += vector_ruido
    elif tipo == "Multiplicativo": imagen_np[D] *= vector_ruido
    
    resultado_np = utilidades.escalar_255(imagen_np)
    
    return resultado_np

def sal_y_pimienta(imagen_np: np.ndarray, p: int) -> np.ndarray:
    """
    Aplica ruido sal y pimienta
    """
    m, n, _ = imagen_np.shape

    for i in range(m):
        for j in range(n):
            x = np.random.rand()
            if x <= p:
                imagen_np[i, j, :] = 0 # pimienta (negro)
            elif x > (1-p):
                imagen_np[i, j, :] = 255 # sal (blanco)

    return imagen_np