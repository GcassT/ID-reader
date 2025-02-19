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
    
    # Añadir estos métodos a tu clase IDImageProcessor

def enhance_image(self, image):
    """
    Mejora la calidad de la imagen para mejor reconocimiento de texto
    """
    # Incrementar el contraste
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced

def deskew_image(self, image):
    """
    Corrige la inclinación de la imagen
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
    
    if lines is not None:
        angle = 0
        for rho, theta in lines[0]:
            angle = theta * 180 / np.pi
            if angle < 45:
                angle = angle
            else:
                angle = angle - 90
                
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), 
                                flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    return image

def to_dataframe(self, id_data):
        """
        Convierte los datos extraídos en un DataFrame
        """
        return pd.DataFrame([id_data])