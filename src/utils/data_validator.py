import re
from datetime import datetime

class IDDataValidator:
    @staticmethod
    def validate_id_number(id_number):
        """
        Valida el formato del número de ID
        """
        if not id_number:
            return False
        # Ajusta esta validación según el formato de tus IDs
        return bool(re.match(r'^\d{8,12}$', id_number))

    @staticmethod
    def validate_date(date_str):
        """
        Valida y formatea fechas
        """
        date_patterns = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y'
        ]
        
        for pattern in date_patterns:
            try:
                return datetime.strptime(date_str, pattern).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None

    @staticmethod
    def clean_text(text):
        """
        Limpia el texto extraído
        """
        # Eliminar caracteres especiales y espacios extras
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        return text