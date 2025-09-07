import numpy as np

# 1. Configuración inicial
#imagen= np.random.randint(0, 256, (4, 4), dtype=np.uint8)
imagen_prueba= np.random.randint(0, 256, (4, 4), dtype=np.uint8)
imagen = np.zeros_like(imagen_prueba)

porcentaje_contaminacion = 50
mu = 0      # Valor medio (µ)
sigma = 30    # Desviación estándar (σ) <--- también es la intensidad del ruido

# 2. Calcular posiciones y valores del ruido
m, n = imagen.shape
num_contaminados = int((porcentaje_contaminacion * m * n) / 100)
print(f"Se contaminarán {num_contaminados} pixeles en la imágen.")

# Elige posiciones aleatorias para el ruido
D = np.unravel_index(np.random.choice(m * n, num_contaminados, replace=False),(m, n))

# Genera los valores de ruido para esas posiciones (esto tendria que hacerlo con mi generador)
ruido = np.random.normal(loc=0, scale=sigma, size=num_contaminados)

# 3. Aplicar el ruido
# Crea una copia de la imagen en formato float para poder operar
imagen_ruidosa = imagen.astype(float)

# Suma el ruido solo en las posiciones elegidas
imagen_ruidosa[D] += ruido

# 4. Finalizar
# Recorta los valores al rango válido [0, 255] y convierte a uint8
imagen_final = np.clip(imagen_ruidosa, 0, 255).astype(np.uint8)


# --- Resultados ---
print("--- Imagen Original ---")
print(imagen)

print("\n--- Imagen Final con Ruido ---")
print(imagen_final)