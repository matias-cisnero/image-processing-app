# 🖼️ Procesamiento de Imágenes con Tkinter

¡Bienvenido! 🎉 Este proyecto es una aplicación en **Tkinter** (Python) para **procesamiento de imágenes y visión por computadora**. Permite aplicar filtros, operadores puntuales, histogramas, ruidos y más, visualizar los resultados y guardarlos fácilmente.

## 📂 Contenido del repositorio

* `procesador_imagenes.py` – Script principal con la interfaz gráfica y todos los filtros disponibles.

* Imágenes RAW para probar:

  * `GIRL.RAW` (389×164)
  * `BARCO.RAW` (290×207)
  * `LENA.RAW` (256×256)
  * `GIRL2.RAW` (256×256)

* Otras imágenes de ejemplo:

  * `barco.png`, `elefante.png`, `TESTpgm.PGM`

* Otros archivos:

  * `README.TXT` – Contiene resolución de las imágenes `.RAW`
  * `.gitignore` y carpetas de ejemplos

## ⚙️ Requisitos

* Python 3.x
* Librerías necesarias:

  * `tkinter` (incluida en la mayoría de instalaciones de Python)
  * `numpy`
  * `Pillow`
  * `Matplotlib`

Instalación rápida:

```bash
pip install -r requirements.txt
```

## 🚀 Cómo ejecutar la aplicación

Desde la terminal:

```bash
python main.py
```

Se abrirá una ventana con opciones para cargar imágenes (`.RAW`, `.PGM`, `.PNG`, `.JPEG`), aplicar filtros, operadores y ruidos, y guardar los resultados.

## ✨ Funcionalidades

### ✅ Operadores puntuales

* Transformación gamma (`γ`)
* Umbralización (`τ`)
* Negativo (`¬`)

### 📊 Histogramas

* RGB y escala de grises
* Ecualización de histograma (`≡`)
* Histogramas de distribución:

  * Gaussiana (`μ`, `σ`)
  * Rayleigh (`σ`)
  * Exponencial (`λ`)

### 🎨 Aplicar ruido

* Gaussiano
* Rayleigh
* Exponencial
* Sal y pimienta

### 🛠️ Filtros

* Media (`M`)
* Mediana (`~x~`)
* Mediana ponderada (`Mₚ`)
* Gaussiano
* Realce de bordes

### 🖱️ Otras herramientas

* Recorte de imágenes
* Visualización y modificación de un pixel
* Restar dos imágenes
* Calcular cantidad de pixeles y promedio de valores en una región