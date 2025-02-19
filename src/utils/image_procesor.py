import cv2
import pytesseract
import numpy as np
from PIL import Image
import pandas as pd
from ..config.settings import TESSERACT_CMD

class IDImageProcessor:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        
    def preprocess_image(self, image):
        """
        Preprocesa la imagen para mejorar la extracción de texto
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        processed = cv2.medianBlur(thresh, 3)
        
        return processed

    def extract_text(self, image_path):
        """
        Extrae texto de la imagen del ID
        """
        # Leer imagen
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")

        # Preprocesar imagen
        processed_image = self.preprocess_image(image)
        
        # Extraer texto
        text = pytesseract.image_to_string(processed_image, lang='spa')
        
        return self.parse_id_data(text)

    def parse_id_data(self, text):
        """
        Analiza el texto extraído y lo estructura en un diccionario
        """
        # Inicializar diccionario de datos
        id_data = {
            'numero_id': None,
            'nombres': None,
            'apellidos': None,
            'fecha_nacimiento': None,
            'fecha_expedicion': None
        }
        
        # Procesar el texto línea por línea
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Aquí agregaremos la lógica para detectar cada campo
            # Este es un ejemplo básico que deberás adaptar según el formato de tus IDs
            if line.isdigit() and len(line) > 8:  # Posible número de ID
                id_data['numero_id'] = line
            # Agregar más lógica de parsing según el formato específico del ID
                
        return id_data

    def to_dataframe(self, id_data):
        """
        Convierte los datos extraídos en un DataFrame
        """
        return pd.DataFrame([id_data])