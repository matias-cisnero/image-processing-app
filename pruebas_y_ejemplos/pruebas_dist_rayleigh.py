import numpy as np
import matplotlib.pyplot as plt

# --- Parámetros de la distribución ---
xi = 2.0         # Parámetro de escala (ξ)
cantidad = 10000  # Cantidad de números a generar

# --- Generación de números aleatorios ---

# a) Generar un solo número
numero_rayleigh_unico = np.random.rayleigh(scale=xi)
print(f"Un solo número aleatorio de Rayleigh: {numero_rayleigh_unico:.4f}\n")

# b) Generar un array de números
numeros_rayleigh = np.random.rayleigh(scale=xi, size=cantidad)
print(f"Muestra de 5 números de Rayleigh:\n{numeros_rayleigh[:5]}\n")

# --- Visualización (opcional) ---
plt.figure(figsize=(8, 5))
plt.hist(numeros_rayleigh, bins=50, density=True, alpha=0.7, label=f'ξ={xi}')
plt.title('Distribución de Rayleigh')
plt.xlabel('Valor')
plt.ylabel('Densidad de Probabilidad')
plt.legend()
plt.grid(True, linestyle='--')
plt.show()