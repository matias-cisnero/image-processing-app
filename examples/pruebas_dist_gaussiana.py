import numpy as np
import matplotlib.pyplot as plt

# --- Parámetros de la distribución ---
mu = 0      # Valor medio (µ)
sigma = 1    # Desviación estándar (σ)
cantidad = 10000  # Cantidad de números a generar

# --- Generación de números aleatorios ---

# a) Generar un solo número
numero_gaussiano_unico = np.random.normal(loc=mu, scale=sigma)
print(f"Un solo número aleatorio Gaussiano: {numero_gaussiano_unico:.4f}\n")

# b) Generar un array (una lista) de números
numeros_gaussianos = np.random.normal(loc=mu, scale=sigma, size=cantidad)
print(f"Muestra de 5 números Gaussianos:\n{numeros_gaussianos[:5]}\n")

# --- Visualización (opcional) ---
plt.figure(figsize=(8, 5))
plt.hist(numeros_gaussianos, bins=50, density=True, alpha=0.7, label=f'µ={mu}, σ={sigma}')
plt.title('Distribución Gaussiana (Normal)')
plt.xlabel('Valor')
plt.ylabel('Densidad de Probabilidad')
plt.legend()
plt.grid(True, linestyle='--')
plt.show()