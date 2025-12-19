import numpy as np
from src import transformaciones, mascaras

def convolucionar(imagen_np: np.ndarray, func_filtro, k=3, modo=0, mediana=False) -> np.ndarray:
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
        resultado_np = transformaciones.escalar_255(imagen_filtrada)
        print("Se aplicó un filtro con modo 0 (escalado)")
    elif modo == 1:
        resultado_np = np.clip(imagen_filtrada, 0, 255).astype(np.uint8)
        print("Se aplicó un filtro con modo 1 (clipeado)")
    elif modo == 2:
        resultado_np = imagen_filtrada
        print("Se aplicó un filtro con modo 2 (np.array)")

    return resultado_np

def _leclerc(gradiente, sigma:int):
    return np.exp((-(gradiente**2))/sigma**2)

def _lorentz(gradiente, sigma:int):
    return 1/(((-(gradiente**2))/sigma**2) + 1)

def difusion(imagen_np: np.ndarray, t: float, sigma: int, isotropico: bool = False, lamb: float = 0.25) -> np.ndarray:
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
                        cN = _leclerc(DN, sigma)
                        cE = _leclerc(DE, sigma)
                        cO = _leclerc(DO, sigma)
                        cS = _leclerc(DS, sigma)

                    # Actualización
                    imagen_filtrada[i, j, c] += lamb * (DN * cN + DE * cE + DO * cO + DS * cS)
    
    resultado_np = transformaciones.escalar_255(imagen_filtrada)
    return resultado_np

def bilateral(imagen_np: np.ndarray, sigma_s: int = 1, sigma_r: int = 1) -> np.ndarray:

    Gs, factor = mascaras.gaussiana(sigma_s)
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
    
    resultado_np = transformaciones.escalar_255(imagen_filtrada)
    return resultado_np