import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_IMAGE_DIR = os.path.join(BASE_DIR, 'input_images')

# Asegurarse que el directorio de imágenes existe
os.makedirs(INPUT_IMAGE_DIR, exist_ok=True)

# Configuración de OCR
TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'tesseract')

# Configuración futura de Redshift
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
REDSHIFT_PORT = os.getenv('REDSHIFT_PORT')
REDSHIFT_DB = os.getenv('REDSHIFT_DB')
REDSHIFT_USER = os.getenv('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')