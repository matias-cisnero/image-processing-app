import numpy as np

def normalizar_a_255(array_np):
    """
    Escala linealmente un array de numpy al rango [0, 255].
    """
    # 1. Encontrar el mínimo y máximo del array
    min_val = np.min(array_np)
    max_val = np.max(array_np)
    
    # 2. Caso especial: si todos los valores son iguales (evitar división por cero)
    if max_val == min_val:
        # Devuelve un array de ceros con la misma forma
        return np.zeros_like(array_np, dtype=np.uint8)
        
    # 3. Aplicar la fórmula de normalización
    array_normalizado = 255 * (array_np - min_val) / (max_val - min_val)
    
    # 4. Convertir a uint8
    return array_normalizado.astype(np.uint8)

# --- Ejemplo de uso ---
# Imagina que esta es tu matriz ruidosa, con valores fuera de rango
matriz_ruidosa = np.array([-50.5, 0, 128.2, 255, 310.0])

# Aplicamos la nueva función en lugar de np.clip()
matriz_final = normalizar_a_255(matriz_ruidosa)

print(f"Array original: {matriz_ruidosa}")
print(f"Mínimo original: {np.min(matriz_ruidosa)}, Máximo original: {np.max(matriz_ruidosa)}\n")

print(f"Array normalizado: {matriz_final}")
print(f"Mínimo final: {np.min(matriz_final)}, Máximo final: {np.max(matriz_final)}")