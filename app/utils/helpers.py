import os
import cv2
from datetime import datetime
import glob
from app.config import VALID_EXTENSIONS

def get_image_files(directory):
    """
    Obtiene todas las imágenes válidas en un directorio
    
    Args:
        directory (str): Directorio a escanear
        
    Returns:
        list: Lista de rutas a archivos de imagen
    """
    if not os.path.exists(directory):
        print(f"Error: El directorio {directory} no existe")
        return []
        
    # Obtener todos los archivos con extensiones válidas
    image_files = []
    for ext in VALID_EXTENSIONS:
        pattern = os.path.join(directory, f"*.{ext}")
        image_files.extend(glob.glob(pattern))
        
    return sorted(image_files)

def create_timestamp_filename(prefix="", suffix="", ext="txt"):
    """
    Crea un nombre de archivo con timestamp
    
    Args:
        prefix (str): Prefijo para el nombre del archivo
        suffix (str): Sufijo para el nombre del archivo
        ext (str): Extensión del archivo sin punto
        
    Returns:
        str: Nombre de archivo con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construir nombre de archivo
    filename_parts = []
    if prefix:
        filename_parts.append(prefix)
    
    filename_parts.append(timestamp)
    
    if suffix:
        filename_parts.append(suffix)
        
    filename = "_".join(filename_parts) + f".{ext}"
    return filename

def resize_image(image, max_width=800):
    """
    Redimensiona una imagen manteniendo su relación de aspecto
    
    Args:
        image (numpy.ndarray): Imagen a redimensionar
        max_width (int): Ancho máximo en píxeles
        
    Returns:
        numpy.ndarray: Imagen redimensionada
    """
    # Si la imagen es más pequeña que max_width, no hacer nada
    h, w = image.shape[:2]
    if w <= max_width:
        return image
        
    # Calcular relación de aspecto
    aspect_ratio = h / w
    
    # Calcular nueva altura
    new_width = max_width
    new_height = int(aspect_ratio * new_width)
    
    # Redimensionar
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized

def print_execution_info():
    """Imprime información sobre la ejecución actual"""
    print(f"ID-Reader - Procesador de Documentos de Identidad")
    print(f"=============================================")
    print(f"Fecha y hora (UTC): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Usuario: {os.getenv('USERNAME', 'Unknown')}")
    print(f"=============================================\n")