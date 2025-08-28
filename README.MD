# Procesamiento de Imágenes con Tkinter

¡Bienvenido! Este proyecto es una aplicación en **Tkinter** (Python) que permite aplicar diversas técnicas de procesamiento digital de imágenes sobre archivos `.RAW` y visualizar los resultados.

## Contenido del repositorio

* `procesador_imagenes.py` – El script principal con la interfaz gráfica y filtros disponibles.
* Archivos de imágenes RAW incluidas para probar:

  * `GIRL.RAW` (389×164)
  * `BARCO.RAW` (290×207)
  * `LENA.RAW` (256×256)
  * `GIRL2.RAW` (256×256)
  * `FRACTAL.RAW` (200×200)
* Imágenes procesadas / ejemplos:

  * `barco.png`, `elefante.png`
* Otros:

  * `README.TXT` (versión anterior)
  * `.gitignore`, `pruebas_y_ejemplos`, y demás archivos útiles.

## Requisitos

* Python 3.x
* Librerías:

  * `tkinter` (normalmente incluida en distribuciones estándar de Python)
  * `numpy`
  * `Pillow` (PIL)

Instalación rápida:

```bash
pip install numpy pillow
```

## Cómo ejecutar la aplicación

Desde la terminal:

```bash
python procesador_imagenes.py
```

Se abrirá una ventana con opciones para cargar imágenes de cualquier tipo (incluido `.RAW` y `.PGM`), aplicar filtros y guardar los resultados.

## Funcionalidades (a personalizar según tu implementación)

* Cargar imágenes en formato RAW.
* Filtros disponibles:

  * En proceso...
* Vista previa en la interfaz y posibilidad de guardar el resultado como imagen (PNG, JPEG, etc.).

