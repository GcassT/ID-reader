#!/usr/bin/env python3
import os
import pandas as pd
from tqdm import tqdm
from app.core.image_processor import ImageProcessor
from app.core.data_extractor import DataExtractor
from app.utils.helpers import get_image_files, print_execution_info
from app.config import INPUT_DIR, OUTPUT_DIR

def process_single_image(image_path, processor, extractor, save_individual=True):
    """
    Procesa una sola imagen
    
    Args:
        image_path (str): Ruta a la imagen
        processor (ImageProcessor): Instancia del procesador de imágenes
        extractor (DataExtractor): Instancia del extractor de datos
        save_individual (bool): Si se debe guardar un CSV individual
        
    Returns:
        pd.DataFrame: DataFrame con los datos extraídos
    """
    filename = os.path.basename(image_path)
    print(f"Procesando imagen: {filename}")
    
    # Procesar imagen
    text, processed_img, annotated_img = processor.process_image(image_path)
    
    if text is None:
        print(f"  Error: No se pudo extraer texto de la imagen")
        return None
        
    # Extraer datos del texto
    extractor.process_text(text, filename=filename)
    
    # Convertir a DataFrame
    df = extractor.to_dataframe()
    
    # Guardar en CSV individual si se solicita
    if save_individual:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        csv_file = f"{base_name}_data.csv"
        extractor.save_to_csv(csv_file)
    
    return df

def main():
    """Función principal"""
    print_execution_info()
    
    # Crear instancias de las clases principales
    processor = ImageProcessor(output_dir=OUTPUT_DIR)
    extractor = DataExtractor(output_dir=OUTPUT_DIR)
    
    # Obtener lista de imágenes a procesar
    image_files = get_image_files(INPUT_DIR)
    
    if not image_files:
        print(f"No se encontraron imágenes en {INPUT_DIR}")
        return
        
    print(f"\nSe encontraron {len(image_files)} imágenes para procesar\n")
    
    # Lista para almacenar todos los DataFrames
    all_data = []
    
    # Procesar cada imagen
    for image_path in tqdm(image_files, desc="Procesando imágenes"):
        df = process_single_image(image_path, processor, extractor)
        if df is not None:
            all_data.append(df)
    
    # Combinar todos los DataFrames
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Combinar datos de anverso y reverso de la misma cédula
        # Toma los valores del anverso para Nombre, Apellido y Documento
        # y los valores del reverso para el resto
        result_df = combined_df.copy()
        
        # Si tenemos datos de la misma persona (anverso y reverso)
        if len(combined_df) > 1 and combined_df.iloc[0]['Documento'] == combined_df.iloc[1]['Documento']:
            # Crear un diccionario con los mejores valores
            best_data = {}
            for column in combined_df.columns:
                # Para cada columna, tomar el primer valor no nulo
                values = combined_df[column].dropna()
                if len(values) > 0:
                    best_data[column] = values.iloc[0]
                else:
                    best_data[column] = None
            
            # Crear un nuevo DataFrame con los mejores valores
            result_df = pd.DataFrame([best_data])
        
        # Guardar el resultado final
        combined_csv = os.path.join(OUTPUT_DIR, 'all_extracted_data.csv')
        result_df.to_csv(combined_csv, index=False)
        print(f"\nDatos combinados guardados en: {combined_csv}")
        
        # Mostrar resumen
        print("\nResumen de datos extraídos:")
        print(result_df)
    else:
        print("\nNo se pudo extraer información de ninguna imagen.")

if __name__ == "__main__":
    main()