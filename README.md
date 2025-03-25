# ID-Reader

Un sistema para analizar y extraer información de documentos de identidad usando procesamiento de imágenes y OCR (Reconocimiento Óptico de Caracteres).

## Características

- Procesa imágenes de documentos de identidad (DNI, cédulas, tarjetas de identificación)
- Extrae información como nombre, apellido, número de documento, fecha de nacimiento
- Guarda la información extraída en formato CSV y DataFrame
- Mejora automáticamente las imágenes para optimizar el OCR
- Permite procesamiento por lotes de múltiples imágenes

## Requisitos

- Python 3.8 o superior
- Tesseract OCR instalado en el sistema
- Dependencias de Python listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/YourUsername/ID-reader.git
   cd ID-reader
   ```

2. Crear un entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Instalar Tesseract OCR:
   - **Windows**: Descargar e instalar desde [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-spa`

4. Configurar el entorno:
   ```bash
   cp .env.example .env
   # Editar .env con la ruta a Tesseract y otras configuraciones
   ```

## Uso

1. Colocar las imágenes de documentos de identidad en la carpeta `data/input`

2. Ejecutar el programa:
   ```bash
   python main.py
   ```

3. Los resultados se guardarán en la carpeta `data/output`:
   - Imágenes procesadas (`processed_*.jpg/png`)
   - Imágenes anotadas con regiones de texto (`annotated_*.jpg/png`)
   - Archivos CSV con datos extraídos por imagen (`*_data.csv`)
   - Archivo CSV combinado con todos los datos (`all_extracted_data.csv`)

## Estructura de datos

El programa extrae la siguiente información de los documentos:

- **Nombre**: Primer nombre de la persona
- **Apellido**: Apellidos de la persona
- **Documento**: Número de documento de identidad
- **Fecha_Nacimiento**: Fecha de nacimiento en formato DD/MM/AAAA
- **Genero**: Género de la persona (M/F)
- **Fecha_Expedicion**: Fecha de expedición del documento
- **Fecha_Vencimiento**: Fecha de vencimiento del documento
- **Timestamp**: Fecha y hora del procesamiento

## Personalización

Puedes ajustar los parámetros de procesamiento editando el archivo `.env` o modificando directamente `app/config.py`.

## Limitaciones

- La precisión del OCR depende de la calidad de la imagen
- El formato de los documentos puede variar, lo que puede requerir ajustes en los patrones de extracción
- El sistema funciona mejor con buena iluminación y documentos bien alineados

## Licencia

[MIT License](LICENSE)