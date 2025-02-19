from utils.image_processor import IDImageProcessor
from utils.logger import logger
import os
from config.settings import INPUT_IMAGE_DIR
import pandas as pd

def main():
    logger.info("Iniciando procesamiento de imágenes")
    
    processor = IDImageProcessor()
    all_data = []
    
    images = [f for f in os.listdir(INPUT_IMAGE_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        logger.warning("No se encontraron imágenes para procesar")
        return
        
    logger.info(f"Se encontraron {len(images)} imágenes para procesar")
    
    for image_name in images:
        logger.info(f"Procesando imagen: {image_name}")
        image_path = os.path.join(INPUT_IMAGE_DIR, image_name)
        
        try:
            id_data = processor.extract_text(image_path)
            df = processor.to_dataframe(id_data)
            all_data.append(df)
            
            logger.info(f"Datos extraídos exitosamente de {image_name}")
            
        except Exception as e:
            logger.error(f"Error procesando {image_name}: {str(e)}")
    
    if all_data:
        # Combinar todos los resultados
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Guardar resultados
        output_path = 'output/processed_ids.csv'
        os.makedirs('output', exist_ok=True)
        final_df.to_csv(output_path, index=False)
        
        logger.info(f"Resultados guardados en {output_path}")
        print("\nResumen de datos procesados:")
        print(final_df)

if __name__ == "__main__":
    main()