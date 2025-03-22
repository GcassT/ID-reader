from datetime import datetime
import os
from utils.image_processor import IDImageProcessor

def main():
    # Mostrar información de ejecución
    print(f"Current Date and Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current User's Login: {os.getenv('USERNAME', 'GcassT')}")
    print("\n" + "="*50 + "\n")
    
    # Inicializar el procesador de imágenes
    processor = IDImageProcessor()
    
    # Listar todas las imágenes en el directorio de entrada
    input_dir = 'input_images'
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Creado directorio: {input_dir}")
        print("Por favor, coloca las imágenes de ID en la carpeta 'input_images'")
        return
        
    images = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        print("No se encontraron imágenes en el directorio input_images/")
        return
        
    print(f"Se encontraron {len(images)} imágenes para procesar")
    
    for image_name in images:
        print(f"\nProcesando imagen: {image_name}")
        image_path = os.path.join(input_dir, image_name)
        
        try:
            # Procesar la imagen y extraer datos
            id_data = processor.extract_text(image_path)
            
            # Convertir a DataFrame
            df = processor.to_dataframe(id_data)
            
            # Mostrar resultados
            print("\nDatos extraídos del ID:")
            print(df)
            
            # Guardar resultados
            output_dir = 'output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_file = f"output/processed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\nResultados guardados en: {output_file}")
            
        except Exception as e:
            print(f"Error al procesar la imagen {image_name}: {str(e)}")

if __name__ == "__main__":
    main()