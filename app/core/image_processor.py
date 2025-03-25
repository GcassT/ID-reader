import cv2
import os
import numpy as np
import pytesseract
from datetime import datetime
import imutils
from app.config import TESSERACT_CMD, OUTPUT_DIR, OCR_CONFIG

# Configurar pytesseract si se ha especificado una ruta
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

class ImageProcessor:
    """Clase para procesar imágenes de documentos de identidad colombianos"""
    
    def __init__(self, output_dir=None):
        """
        Inicializa el procesador de imágenes
        
        Args:
            output_dir (str, optional): Directorio para guardar resultados.
                                        Por defecto usa el valor de config.OUTPUT_DIR
        """
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_image(self, image_path):
        """
        Carga una imagen desde un archivo
        
        Args:
            image_path (str): Ruta a la imagen a cargar
            
        Returns:
            numpy.ndarray: Imagen cargada o None si hubo error
        """
        if not os.path.exists(image_path):
            print(f"Error: No se encuentra la imagen en {image_path}")
            return None
            
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: No se pudo cargar la imagen {image_path}")
            return None
            
        return image
        
    def auto_rotate(self, image):
        """
        Detecta y corrige la orientación de la imagen
        
        Args:
            image (numpy.ndarray): Imagen original
            
        Returns:
            numpy.ndarray: Imagen rotada correctamente
        """
        # Crear copias para probar diferentes rotaciones
        rotations = []
        scores = []
        
        # Probar imagen original
        rotations.append(image)
        
        # Probar 90, 180 y 270 grados
        for angle in [90, 180, 270]:
            rotated = imutils.rotate_bound(image, angle)
            rotations.append(rotated)
        
        # También probar imagen volteada (para casos donde el documento está boca abajo)
        flipped = cv2.flip(image, -1)  # Voltear tanto horizontal como verticalmente
        rotations.append(flipped)
        
        # Evaluar cada rotación
        for i, img in enumerate(rotations):
            # Convertir a escala de grises y binarizar
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            
            # Guardar temporalmente para comprobación visual
            temp_path = os.path.join(self.output_dir, f"rotation_{i}.jpg")
            cv2.imwrite(temp_path, img)
            
            # Extraer texto para evaluar
            text = pytesseract.image_to_string(thresh, config='--psm 11 --oem 3 -l spa')
            
            # Contar palabras clave comunes en cédulas colombianas
            keywords = ['REPUBLICA', 'COLOMBIA', 'CEDULA', 'CIUDADANIA', 'IDENTIDAD', 'PERSONAL', 
                        'FECHA', 'NACIMIENTO', 'EXPEDICION', 'SEXO', 'LUGAR']
            score = sum(1 for keyword in keywords if keyword in text.upper())
            
            # Guardar puntuación
            scores.append(score)
            
        # Obtener la rotación con mayor puntuación
        best_idx = np.argmax(scores)
        best_rotation = rotations[best_idx]
        
        print(f"Se aplicó rotación automática. Mejor orientación: {best_idx * 90 if best_idx < 4 else 'Volteada'}")
        
        return best_rotation
        
    def is_reverse_side(self, image_path):
        """
        Determina si la imagen es el reverso de una cédula colombiana
        
        Args:
            image_path (str): Ruta a la imagen
        
        Returns:
            bool: True si es reverso, False si es anverso
        """
        # Implementación sencilla: si el nombre del archivo contiene 'reverso' o 'back'
        filename = os.path.basename(image_path).lower()
        if 'reverso' in filename or 'back' in filename or 'trasera' in filename or 'reverse' in filename:
            return True
            
        # También podemos intentar detectar basado en características visuales
        image = self.load_image(image_path)
        if image is None:
            return False
            
        # Convertir a escala de grises y extraer texto
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 11 --oem 3 -l spa')
        
        # Palabras clave que aparecen en el reverso de cédulas colombianas
        reverse_keywords = ['NACIMIENTO', 'FECHA', 'SEXO', 'BLOOD', 'GRUPO', 'SANGUINEO', 'RH',
                          'EXPEDICION', 'LUGAR', 'ESTATURA']
        front_keywords = ['REPUBLICA', 'COLOMBIA', 'CEDULA', 'CIUDADANIA']
        
        # Contar palabras clave de cada tipo
        reverse_score = sum(1 for keyword in reverse_keywords if keyword in text.upper())
        front_score = sum(1 for keyword in front_keywords if keyword in text.upper())
        
        # Si hay más palabras clave del reverso que del anverso, probablemente es el reverso
        return reverse_score > front_score
        
    def preprocess_for_colombian_id(self, image, is_reverse=False):
        """
        Preprocesamiento específico para cédulas colombianas
        
        Args:
            image (numpy.ndarray): Imagen a preprocesar
            is_reverse (bool): Si es el reverso de la cédula
            
        Returns:
            numpy.ndarray: Imagen preprocesada
        """
        # Auto-rotar la imagen si es necesario
        rotated = self.auto_rotate(image)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
        
        if is_reverse:
            # Para el reverso, aplicar un procesamiento más agresivo para separar el texto
            # del fondo con patrones de seguridad
            
            # Paso 1: Aumentar contraste drásticamente
            alpha = 2.5  # Contraste (1.0-3.0)
            beta = 30    # Brillo (0-100)
            adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
            
            # Paso 2: Filtro bilateral para preservar bordes pero eliminar ruido
            filtered = cv2.bilateralFilter(adjusted, 11, 17, 17)
            
            # Paso 3: Umbral adaptativo específico para reverso
            binary = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY, 15, 5
            )
            
            # Paso 4: Aplicar operaciones morfológicas más agresivas para limpiar ruido
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            # Paso 5: Invertir la imagen (ya que a veces el texto es más claro que el fondo)
            inverted = cv2.bitwise_not(processed)
            
            # Devolver ambas versiones (normal e invertida) para procesamiento posterior
            return rotated, processed, inverted
        else:
            # Para el anverso, usar el procesamiento estándar
            
            # Ajustar el brillo y contraste
            alpha = 1.5  # Contraste
            beta = 15    # Brillo
            adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
            
            # Aplicar un desenfoque para reducir ruido
            blurred = cv2.GaussianBlur(adjusted, (3, 3), 0)
            
            # Aplicar umbral adaptativo para binarizar
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Operaciones morfológicas para limpiar ruido
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            return rotated, processed, None
        
    def process_image(self, image_path, save_intermediate=True):
        """
        Procesa una imagen para extraer texto mediante OCR
        
        Args:
            image_path (str): Ruta a la imagen a procesar
            save_intermediate (bool): Si se deben guardar imágenes intermedias
            
        Returns:
            tuple: (texto_extraído, imagen_procesada, imagen_con_anotaciones)
        """
        # Cargar imagen
        original_image = self.load_image(image_path)
        if original_image is None:
            return None, None, None
            
        # Determinar si es el anverso o el reverso
        is_reverse = self.is_reverse_side(image_path)
        if is_reverse:
            print(f"Detectada como reverso de cédula colombiana.")
            
        # Preprocesar imagen específicamente para cédulas colombianas
        rotated_image, processed_image, inverted_image = self.preprocess_for_colombian_id(original_image, is_reverse)
        
        # Guardar imagen procesada si se solicita
        if save_intermediate:
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, f"processed_{filename}")
            cv2.imwrite(output_path, processed_image)
            print(f"Imagen procesada guardada en: {output_path}")
            
            # También guardar la imagen rotada
            rotated_path = os.path.join(self.output_dir, f"rotated_{filename}")
            cv2.imwrite(rotated_path, rotated_image)
            print(f"Imagen rotada guardada en: {rotated_path}")
            
            # Si hay imagen invertida, guardarla también
            if inverted_image is not None:
                inverted_path = os.path.join(self.output_dir, f"inverted_{filename}")
                cv2.imwrite(inverted_path, inverted_image)
                print(f"Imagen invertida guardada en: {inverted_path}")
            
        # Extraer texto con OCR - MÚLTIPLES ESTRATEGIAS
        extracted_text = ""
        best_text = ""
        max_keywords = 0
        
        # Configuraciones específicas para cédula colombiana
        psm_configs = [3, 4, 6, 11]  # Diferentes modos de segmentación de página
        try:
            # Preparar listas de palabras clave según si es anverso o reverso
            if is_reverse:
                keywords = ['FECHA', 'NACIMIENTO', 'EXPEDICION', 'SEXO', 'LUGAR', 'ESTATURA', 'GRUPO', 'RH']
            else:
                keywords = ['REPUBLICA', 'COLOMBIA', 'CEDULA', 'CIUDADANIA', 'IDENTIDAD', 'PERSONAL']
                
            # Probar diferentes configuraciones y quedarse con la mejor
            for psm in psm_configs:
                # Configuración actual
                config = f'--psm {psm} --oem 3 -l spa'
                
                # Extraer texto de la imagen procesada
                text = pytesseract.image_to_string(processed_image, config=config)
                
                # Evaluar calidad del texto extraído
                score = sum(1 for keyword in keywords if keyword in text.upper())
                
                # Guardar el mejor resultado
                if score > max_keywords:
                    max_keywords = score
                    best_text = text
                
                # Acumular todo el texto
                extracted_text += "\n\n--- PSM " + str(psm) + " ---\n" + text
                
                # Si es el reverso, también intentar con la imagen invertida
                if is_reverse and inverted_image is not None:
                    text_inv = pytesseract.image_to_string(inverted_image, config=config)
                    score_inv = sum(1 for keyword in keywords if keyword in text_inv.upper())
                    
                    if score_inv > max_keywords:
                        max_keywords = score_inv
                        best_text = text_inv
                        
                    extracted_text += "\n\n--- INVERTED PSM " + str(psm) + " ---\n" + text_inv
            
            # Si no se detectaron suficientes palabras clave, intentar con la imagen rotada
            if max_keywords < 2:
                print("Pocas palabras clave detectadas, intentando con imagen rotada...")
                # Probar imagen rotada directamente
                for psm in psm_configs:
                    config = f'--psm {psm} --oem 3 -l spa'
                    text = pytesseract.image_to_string(rotated_image, config=config)
                    
                    # Evaluar calidad
                    score = sum(1 for keyword in keywords if keyword in text.upper())
                    
                    if score > max_keywords:
                        max_keywords = score
                        best_text = text
                    
                    # Acumular texto
                    extracted_text += "\n\n--- ROTATED PSM " + str(psm) + " ---\n" + text
            
            # También intentar con el negativo de la imagen (a veces funciona mejor)
            negative = cv2.bitwise_not(processed_image)
            text = pytesseract.image_to_string(negative, config='--psm 3 --oem 3 -l spa')
            
            score = sum(1 for keyword in keywords if keyword in text.upper())
            if score > max_keywords:
                max_keywords = score
                best_text = text
                
            extracted_text += "\n\n--- NEGATIVE ---\n" + text
            
            # Para el reverso, intentar una segmentación más agresiva
            if is_reverse:
                # Intentar con análisis de bloques de texto
                text = pytesseract.image_to_string(processed_image, config='--psm 1 --oem 3 -l spa')
                score = sum(1 for keyword in keywords if keyword in text.upper())
                
                if score > max_keywords:
                    max_keywords = score
                    best_text = text
                    
                extracted_text += "\n\n--- BLOCK MODE ---\n" + text
            
            # Imprimir el texto extraído para depuración
            print("\n--- TEXTO EXTRAÍDO POR OCR (PARA DEPURACIÓN) ---")
            print(best_text)
            print("--- FIN TEXTO OCR ---\n")
            
            # Guardar todo el texto en archivo para análisis
            text_file = os.path.join(self.output_dir, f"ocr_text_{os.path.splitext(os.path.basename(image_path))[0]}.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write("--- MEJOR TEXTO ---\n")
                f.write(best_text)
                f.write("\n\n--- TODOS LOS INTENTOS ---\n")
                f.write(extracted_text)
            print(f"Texto OCR guardado en: {text_file}")
            
        except Exception as e:
            print(f"Error en OCR: {str(e)}")
            return None, processed_image, None
            
        # Crear imagen con anotaciones
        annotated_image = rotated_image.copy()
        
        # Detectar y marcar regiones de texto
        try:
            gray = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Encontrar contornos en la imagen
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos por tamaño
            min_area = 500  # Ajustar según el tamaño de la imagen
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w * h > min_area:
                    # Dibujar rectángulo
                    cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        except Exception as e:
            print(f"Error al anotar la imagen: {str(e)}")
            
        # Guardar imagen anotada
        if save_intermediate:
            annotated_path = os.path.join(self.output_dir, f"annotated_{os.path.basename(image_path)}")
            cv2.imwrite(annotated_path, annotated_image)
            print(f"Imagen anotada guardada en: {annotated_path}")
            
        return best_text, processed_image, annotated_image