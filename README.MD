# 🖼️ Procesamiento de Imágenes con Tkinter

¡Bienvenido! 🎉 Este proyecto es una aplicación en **Tkinter** (Python) que permite aplicar diversas técnicas de **procesamiento de imágenes**, visualizar los resultados y guardarlos de forma sencilla.

## 📂 Contenido del repositorio

* `procesador_imagenes.py` – El script principal con la interfaz gráfica y filtros disponibles.
* Archivos de imágenes RAW incluidas para probar:

  * `GIRL.RAW` (389×164)
  * `BARCO.RAW` (290×207)
  * `LENA.RAW` (256×256)
  * `GIRL2.RAW` (256×256)
  * `FRACTAL.RAW` (200×200)
* 🖼️ Otras imágenes de ejemplo:

  * `barco.png`, `elefante.png`
* 📑 Otros:

  * `README.TXT` (contiene la resolución de las imágenes `.RAW`)
  * `.gitignore`, `pruebas_y_ejemplos`, y demás archivos útiles.

## ⚙️ Requisitos

* Python 3.x
* Librerías necesarias:

  * `tkinter` (incluida por defecto en la mayoría de instalaciones de Python)
  * `numpy`
  * `Pillow` (PIL)

Instalación rápida:

```bash
pip install numpy pillow
```

## 🚀 Cómo ejecutar la aplicación

Desde la terminal:

```bash
python procesador_imagenes.py
```

Se abrirá una ventana con opciones para cargar imágenes de distintos formatos (`.RAW`, `.PGM`, `.PNG`, etc.), aplicar filtros y guardar los resultados.

## ✨ Funcionalidades (en desarrollo)

✅ Cargar imágenes en formato **RAW** y otros comunes (PNG, JPEG, PGM...).
✅ Vista previa de la imagen cargada.
✅ Guardar la imagen procesada en distintos formatos.
✅ Realizar un recorte de la imágen.
✅ Ver y modificar el valor de un pixel en una imagen.
✅ Restar dos imágenes.
✅ Informar la cantidad de pixels y promedio de sus valores en una región de la imágen.
🛠️ Filtros disponibles (en progreso):

* ...