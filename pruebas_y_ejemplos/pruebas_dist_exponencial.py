import numpy as np
import matplotlib.pyplot as plt

# --- Parámetros de la distribución ---
lambda_param = 0.5   # Parámetro de tasa (λ)
cantidad = 10000      # Cantidad de números a generar

# Convertimos lambda (tasa) al parámetro scale (escala) que necesita NumPy
scale_param = 1 / lambda_param  # scale = 1 / 0.5 = 2.0

# --- Generación de números aleatorios ---

# a) Generar un solo número
numero_exponencial_unico = np.random.exponential(scale=scale_param)
print(f"Un solo número aleatorio Exponencial: {numero_exponencial_unico:.4f}\n")

# b) Generar un array de números
numeros_exponenciales = np.random.exponential(scale=scale_param, size=cantidad)
print(f"Muestra de 5 números Exponenciales:\n{numeros_exponenciales[:5]}\n")

# --- Visualización (opcional) ---
plt.figure(figsize=(8, 5))
plt.hist(numeros_exponenciales, bins=50, density=True, alpha=0.7, label=f'λ={lambda_param}, scale={scale_param}')
plt.title('Distribución Exponencial')
plt.xlabel('Valor')
plt.ylabel('Densidad de Probabilidad')
plt.legend()
plt.grid(True, linestyle='--')
plt.show()