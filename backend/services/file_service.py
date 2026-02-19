import os
import time
from typing import Optional


class FileService:
    """
    Servicio para gestión de archivos temporales.
    
    Maneja el almacenamiento temporal de archivos generados y proporciona
    funcionalidad de limpieza automática de archivos antiguos.
    """
    
    def __init__(self, storage_path: str, cleanup_hours: int = 24):
        """
        Inicializa el servicio de archivos.
        
        Args:
            storage_path: Ruta del directorio de almacenamiento temporal
            cleanup_hours: Número de horas después de las cuales los archivos son considerados antiguos
        """
        self.storage_path = storage_path
        self.cleanup_hours = cleanup_hours
        os.makedirs(storage_path, exist_ok=True)
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """
        Retorna la ruta completa de un archivo si existe.
        
        Args:
            filename: Nombre del archivo a buscar
            
        Returns:
            Ruta completa del archivo si existe, None en caso contrario
        """
        file_path = os.path.join(self.storage_path, filename)
        if os.path.exists(file_path):
            return file_path
        return None
    
    def cleanup_old_files(self):
        """
        Elimina archivos más antiguos que cleanup_hours.
        
        Itera sobre todos los archivos en el directorio de almacenamiento
        y elimina aquellos cuya fecha de modificación es anterior al umbral
        configurado.
        """
        now = time.time()
        cutoff = now - (self.cleanup_hours * 3600)
        
        for filename in os.listdir(self.storage_path):
            file_path = os.path.join(self.storage_path, filename)
            if os.path.isfile(file_path):
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error eliminando {filename}: {e}")
