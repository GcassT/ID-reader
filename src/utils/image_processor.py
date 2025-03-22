import cv2
import pytesseract
import numpy as np
from PIL import Image
import pandas as pd
import os
from dotenv import load_dotenv
import re
from datetime import datetime

class IDImageProcessor:
    def __init__(self):
        # ... (mantener el código de inicialización existente) ...
        pass

    def parse_id_data(self, text):
        """
        Analiza el texto extraído de una cédula colombiana
        """
        # Inicializar diccionario de datos
        id_data = {
            'numero_id': None,
            'nombres': None,
            'apellidos': None,
            'fecha_nacimiento': None,
            'fecha_expedicion': None
        }
        
        # Convertir el texto a líneas y eliminar espacios en blanco
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        print("Texto extraído de la imagen:")
        print("-------------------")
        print(text)
        print("-------------------")

        # Patrones para identificar campos
        patterns = {
            'numero_id': r'\b\d{8,11}\b',  # 8-11 dígitos consecutivos
            'fecha': r'\b\d{1,2}-[A-Za-z]{3,4}-\d{4}\b',  # formato: DD-MMM-YYYY
        }

        # Buscar número de cédula
        for line in lines:
            if re.search(patterns['numero_id'], line):
                id_data['numero_id'] = re.search(patterns['numero_id'], line).group()
                break

        # Variables para almacenar nombres y apellidos temporalmente
        nombres_temp = []
        apellidos_temp = []
        found_nombres = False

        for i, line in enumerate(lines):
            # Ignorar líneas comunes que no son relevantes
            if any(keyword in line.upper() for keyword in ['REPUBLICA', 'COLOMBIA', 'CEDULA', 'IDENTIFICACION']):
                continue

            # Buscar fechas
            fecha_match = re.search(patterns['fecha'], line)
            if fecha_match:
                fecha = fecha_match.group()
                if 'FECHA DE NACIMIENTO' in line.upper() or 'NACIMIENTO' in line.upper():
                    id_data['fecha_nacimiento'] = fecha
                elif 'FECHA DE EXPEDICION' in line.upper() or 'EXPEDICION' in line.upper():
                    id_data['fecha_expedicion'] = fecha
                continue

            # Procesar nombres y apellidos
            if 'APELLIDOS' in line.upper() or found_nombres:
                found_nombres = True
                current_line = line.upper().replace('APELLIDOS', '').replace('NOMBRES', '').strip()
                if current_line:
                    if not id_data['apellidos']:
                        apellidos_temp.append(current_line)
                    elif not id_data['nombres']:
                        nombres_temp.append(current_line)

        # Combinar nombres y apellidos
        if apellidos_temp:
            id_data['apellidos'] = ' '.join(apellidos_temp)
        if nombres_temp:
            id_data['nombres'] = ' '.join(nombres_temp)

        return id_data

    def preprocess_image(self, image):
        """
        Mejora el preprocesamiento de la imagen para mejor OCR
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aumentar el contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Eliminar ruido
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Binarización adaptativa
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Dilatación para mejorar la conectividad de los caracteres
        kernel = np.ones((1,1), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return dilated

    def extract_text(self, image_path):
        """
        Extrae texto de la imagen con configuración mejorada
        """
        # Leer imagen
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")

        # Preprocesar imagen
        processed_image = self.preprocess_image(image)
        
        # Guardar imagen procesada para debug
        debug_path = 'output/processed_image.png'
        os.makedirs('output', exist_ok=True)
        cv2.imwrite(debug_path, processed_image)
        print(f"Imagen procesada guardada en: {debug_path}")

        # Configuración de OCR
        custom_config = r'--oem 3 --psm 3'
        try:
            text = pytesseract.image_to_string(
                processed_image, 
                lang='spa',
                config=custom_config
            )
        except Exception as e:
            print(f"Error en OCR: {str(e)}")
            return None
        
        return self.parse_id_data(text)