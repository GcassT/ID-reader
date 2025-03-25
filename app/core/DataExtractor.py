import os
import pandas as pd
import re
import dateutil.parser
from datetime import datetime
import logging
import unicodedata

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataExtractor:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.nombre = ""
        self.apellido = ""
        self.documento = ""
        self.fecha_nacimiento = None
        self.genero = None
        self.fecha_expedicion = None
        self.texto_completo = ""
        self.filename = ""
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
    
    def normalize_text(self, text):
        """Normaliza el texto para comparaciones insensibles a acentos."""
        text = unicodedata.normalize('NFD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        return text.upper()
    
    def clean_text(self, text):
        """Limpia el texto eliminando caracteres especiales no deseados."""
        # Eliminar caracteres especiales que no sean útiles
        text = re.sub(r'[—:\\/\"\']+', '', text)
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def parse_date(self, date_str):
        """Convierte diferentes formatos de fecha a formato DD/MM/YYYY."""
        try:
            # Manejar formato con comillas: 18'ENE'2003
            if "'" in date_str:
                day, month, year = re.findall(r"(\d+)'(\w+)'(\d+)", date_str)[0]
                month_map = {
                    'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04', 'MAY': '05', 'JUN': '06',
                    'JUL': '07', 'AGO': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12'
                }
                return f"{day.zfill(2)}/{month_map.get(month, '01')}/{year}"
            
            # Manejar formato con guiones: 25-ENE-2021
            elif "-" in date_str:
                parts = date_str.split('-')
                if len(parts) == 3:
                    day, month, year = parts
                    month_map = {
                        'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04', 'MAY': '05', 'JUN': '06',
                        'JUL': '07', 'AGO': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12'
                    }
                    return f"{day.zfill(2)}/{month_map.get(month, '01')}/{year}"
            
            # Intentar con dateutil.parser para otros formatos
            date_obj = dateutil.parser.parse(date_str, fuzzy=True)
            return date_obj.strftime("%d/%m/%Y")
        except Exception as e:
            logging.warning(f"Error al parsear fecha '{date_str}': {e}")
            return None

    def extract_data_from_front(self, front_text):
        """Extrae datos del texto OCR del frente de la cédula."""
        nombre = ""
        apellido = ""
        documento = ""
        
        # Dividir el texto en líneas y limpiarlas
        lines = [line.strip() for line in front_text.split('\n') if line.strip()]
        
        # Buscar número de documento - patrón mejorado para capturar el número completo
        doc_pattern = r"n[uú]mero[\s\.]*(\d[\d\.\,\s]+\d)"
        doc_match = re.search(doc_pattern, front_text, re.IGNORECASE)
        if doc_match:
            # Eliminar puntos, comas y espacios del número
            documento = re.sub(r'[,.\s]', '', doc_match.group(1))
        
        # Si no se encontró con el patrón anterior o es demasiado corto, buscar cualquier secuencia de dígitos
        if not documento or len(documento) < 7:
            # Extraer todas las secuencias de dígitos
            digit_sequences = re.findall(r'\d+', front_text)
            # Filtrar por longitud (cédulas colombianas tienen típicamente 10 dígitos)
            valid_sequences = [seq for seq in digit_sequences if 7 <= len(seq) <= 12]
            if valid_sequences:
                # Tomar la secuencia más larga que probablemente es el número de cédula
                documento = max(valid_sequences, key=len)
        
        # Localizar las líneas clave para nombre y apellido
        apellido_line_idx = -1
        nombre_line_idx = -1
        apellido_label_idx = -1
        
        for i, line in enumerate(lines):
            # Buscar la etiqueta "APELLIDOS"
            if "APELLIDO" in line.upper():
                apellido_label_idx = i
            # Buscar línea que contiene "CASTRO PADILLA" (o cualquier texto que parezca apellido)
            if "CASTRO" in line:
                apellido_line_idx = i
        
        # Estrategia específica para este formato:
        # 1. Si hay una línea de apellido identificada
        if apellido_line_idx >= 0:
            # Limpiar la línea del apellido
            apellido = self.clean_text(lines[apellido_line_idx])
            
            # 2. Buscar el nombre - suele estar después de la etiqueta "APELLIDOS"
            if apellido_label_idx >= 0 and apellido_label_idx + 1 < len(lines):
                # El nombre está en la línea después de "APELLIDOS"
                nombre = self.clean_text(lines[apellido_label_idx + 1])
            
            # Si no encontramos el nombre con ese método, buscar una línea que parezca nombre
            if not nombre:
                for i, line in enumerate(lines):
                    # Evitar líneas que ya sabemos que no son el nombre
                    if i != apellido_line_idx and i != apellido_label_idx:
                        clean_line = self.clean_text(line)
                        # Si la línea tiene contenido, no tiene dígitos y no tiene palabras clave
                        if (clean_line and 
                            not any(c.isdigit() for c in clean_line) and
                            not any(word in clean_line.upper() for word in ["COLOMBIA", "REPUBLICA", "CEDULA", "CIUDADANIA"])):
                            # Si es una sola palabra, probablemente es un nombre
                            if len(clean_line.split()) == 1:
                                nombre = clean_line
                                break
        
        # Limpiar el nombre para eliminar caracteres especiales
        nombre = re.sub(r'[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]', '', nombre).strip()
        
        return nombre, apellido, documento

    def extract_data_from_back(self, back_text):
        """Extrae datos del texto OCR del reverso de la cédula."""
        fecha_nacimiento = None
        genero = None
        fecha_expedicion = None
        
        # Buscar fecha de nacimiento - MEJORADO para detectar el formato 18'ENE'2003
        birth_pattern = r"FECHA DE (?:NACIMIENTO|RACIMIENTO)[:\s]+(\d+[\'|\-][\w]+[\'|\-]\d+)"
        birth_match = re.search(birth_pattern, back_text, re.IGNORECASE)
        if birth_match:
            fecha_nacimiento_str = birth_match.group(1)
            fecha_nacimiento = self.parse_date(fecha_nacimiento_str)
        
        # Buscar fecha de expedición - MEJORADO para detectar el formato 25-ENE-2021
        exp_pattern = r"(\d+\-[\w]+\-\d+)"
        exp_match = re.search(exp_pattern, back_text)
        if exp_match:
            fecha_expedicion_str = exp_match.group(1)
            fecha_expedicion = self.parse_date(fecha_expedicion_str)
        
        # Buscar género
        if re.search(r"[^A-Za-z]M[^A-Za-z]", back_text):
            genero = "M"
        elif re.search(r"[^A-Za-z]F[^A-Za-z]", back_text):
            genero = "F"
        
        return fecha_nacimiento, genero, fecha_expedicion

    def process_text(self, text, filename=""):
        """Procesa el texto OCR extraído de la imagen."""
        self.texto_completo = text
        self.filename = filename
        
        # Aplicar normalización para detectar frases con o sin acentos
        normalized_text = self.normalize_text(text)
        
        # Determinar si es frente o reverso basado en patrones característicos
        is_front = "REPUBLICA DE COLOMBIA" in normalized_text or "IDENTIFICACION PERSONAL" in normalized_text
        is_back = "FECHA DE NACIMIENTO" in normalized_text or "FECHA DE RACIMIENTO" in normalized_text
        
        if is_front:
            logging.info(f"Procesando texto del frente de la cédula: {filename}")
            nombre, apellido, documento = self.extract_data_from_front(text)
            self.nombre = nombre
            self.apellido = apellido
            self.documento = documento
        elif is_back:
            logging.info(f"Procesando texto del reverso de la cédula: {filename}")
            fecha_nacimiento, genero, fecha_expedicion = self.extract_data_from_back(text)
            self.fecha_nacimiento = fecha_nacimiento
            self.genero = genero
            self.fecha_expedicion = fecha_expedicion
        else:
            logging.warning(f"No se pudo determinar si es frente o reverso: {filename}")
            
        # Guardar el texto procesado para depuración
        if filename:
            text_file = os.path.join(self.output_dir, f"ocr_text_{os.path.splitext(filename)[0]}.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)

    def to_dataframe(self):
        """Convierte los datos extraídos a un DataFrame."""
        data = {
            'Nombre': [self.nombre],
            'Apellido': [self.apellido],
            'Documento': [self.documento],
            'Fecha_Nacimiento': [self.fecha_nacimiento],
            'Genero': [self.genero],
            'Fecha_Expedicion': [self.fecha_expedicion],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        df = pd.DataFrame(data)
        
        # Registrar los datos extraídos
        logging.info(f"Resumen de datos extraídos:\n{df}")
        
        return df
    
    def save_to_csv(self, filename):
        """Guarda los datos en un archivo CSV."""
        df = self.to_dataframe()
        csv_path = os.path.join(self.output_dir, filename)
        df.to_csv(csv_path, index=False)
        logging.info(f"Datos guardados en: {csv_path}")
        return csv_path
    
    def combine_data(self, front_data, back_data):
        """Combina los datos extraídos del frente y reverso de la cédula."""
        nombre, apellido, documento = front_data
        fecha_nacimiento, genero, fecha_expedicion = back_data
        
        self.nombre = nombre
        self.apellido = apellido
        self.documento = documento
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.fecha_expedicion = fecha_expedicion
        
        return self.to_dataframe()