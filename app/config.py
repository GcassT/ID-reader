import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Directorios - Configuración ajustada a tus carpetas existentes
INPUT_DIR = os.getenv('INPUT_DIR', 'input_images')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'OUTPUT')

# Resto del código de configuración permanece igual...
TESSERACT_CMD = os.getenv('TESSERACT_CMD', '')
TESSERACT_LANG = os.getenv('TESSERACT_LANG', 'spa')
VALID_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tif', 'tiff'}
OCR_CONFIG = f'--psm 3 --oem 3 -l {TESSERACT_LANG}'
MIN_CONFIDENCE = int(os.getenv('MIN_CONFIDENCE', 60))

# Crear directorios si no existen
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)