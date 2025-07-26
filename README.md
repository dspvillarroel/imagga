# WebApp Dockerizada con Imagga

Esta aplicación web Dockerizada utiliza el servicio SaaS de Imagga para analizar imágenes y mostrar etiquetas de clasificación. Permite subir imágenes, analizarlas en tiempo real y ver un historial de análisis previos.

## Requisitos
- Docker instalado (Windows | Mac | Linux)

- Cuenta en Imagga (gratuita)

- Credenciales de API de Imagga (API Key y API Secret)

## Instrucciones de instalación
1. git clone https://github.com/dspvillarroel/imagga.git
cd imagga-docker-app

2. Construir la Imagen de Docker
- docker build -t imagga-app .

3. Ejecutar el contenedor
- docker run -d -p 5000:5000 \
  -e IMAGGA_API_KEY="TU_API_KEY" \
  -e IMAGGA_API_SECRET="TU_API_SECRET" \
  -v ./uploads:/app/uploads \
  imagga-app
4.  Acceder a la aplicación
- http://localhost:5000

## Uso de la aplicación
 Subir imágenes:

1. Haz clic en "Seleccionar archivos" y elige hasta 3 imágenes (formatos soportados: JPG, PNG, GIF)

2. Haz clic en "Subir y Analizar"

3. Ver resultados:

- Las imágenes subidas se mostrarán con sus etiquetas de clasificación

4. Las dos etiquetas con mayor porcentaje de confianza aparecerán bajo cada imagen

5. Ver historial:

- Haz clic en "Mostrar Historial" para ver todas las imágenes analizadas previamente