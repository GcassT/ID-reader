from utils.image_processor import IDImageProcessor
import os
from config.settings import INPUT_IMAGE_DIR

def main():
    # Inicializar el procesador de imágenes
    processor = IDImageProcessor()
    
    # Para pruebas, procesamos una imagen específica
    # Asegúrate de tener una imagen de prueba en el directorio input_images
    test_image = "test_id.jpg"  # Reemplaza con el nombre de tu imagen de prueba
    image_path = os.path.join(INPUT_IMAGE_DIR, test_image)
    
    try:
        # Procesar la imagen y extraer datos
        id_data = processor.extract_text(image_path)
        
        # Convertir a DataFrame
        df = processor.to_dataframe(id_data)
        
        # Mostrar resultados
        print("\nDatos extraídos del ID:")
        print(df)
        
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")

if __name__ == "__main__":
    main()