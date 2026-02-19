import pytest
import os
import time
import tempfile
import shutil
from services.file_service import FileService


class TestFileService:
    """Pruebas unitarias para FileService"""
    
    @pytest.fixture
    def temp_dir(self):
        """Crea un directorio temporal para las pruebas"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Limpiar después de las pruebas
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
    
    def test_init_creates_storage_directory(self, temp_dir):
        """Verificar que __init__ crea el directorio de almacenamiento"""
        storage_path = os.path.join(temp_dir, "new_storage")
        file_service = FileService(storage_path)
        
        assert os.path.exists(storage_path)
        assert os.path.isdir(storage_path)
    
    def test_init_with_existing_directory(self, temp_dir):
        """Verificar que __init__ funciona con directorio existente"""
        # El directorio ya existe
        file_service = FileService(temp_dir)
        
        assert os.path.exists(temp_dir)
        assert file_service.storage_path == temp_dir
    
    def test_init_sets_cleanup_hours(self, temp_dir):
        """Verificar que __init__ configura cleanup_hours correctamente"""
        file_service = FileService(temp_dir, cleanup_hours=48)
        
        assert file_service.cleanup_hours == 48
    
    def test_init_default_cleanup_hours(self, temp_dir):
        """Verificar que cleanup_hours tiene valor por defecto de 24"""
        file_service = FileService(temp_dir)
        
        assert file_service.cleanup_hours == 24
    
    def test_get_file_path_with_existing_file(self, temp_dir):
        """Caso: archivo existe, debe retornar ruta completa"""
        file_service = FileService(temp_dir)
        
        # Crear un archivo de prueba
        test_filename = "test_file.pdf"
        test_file_path = os.path.join(temp_dir, test_filename)
        with open(test_file_path, 'w') as f:
            f.write("test content")
        
        result = file_service.get_file_path(test_filename)
        
        assert result == test_file_path
        assert os.path.exists(result)
    
    def test_get_file_path_with_nonexistent_file(self, temp_dir):
        """Caso: archivo no existe, debe retornar None"""
        file_service = FileService(temp_dir)
        
        result = file_service.get_file_path("nonexistent_file.pdf")
        
        assert result is None
    
    def test_get_file_path_with_empty_filename(self, temp_dir):
        """Caso edge: nombre de archivo vacío retorna el directorio si existe"""
        file_service = FileService(temp_dir)
        
        result = file_service.get_file_path("")
        
        # Con nombre vacío, os.path.join retorna el directorio mismo
        # que existe, por lo que retorna la ruta del directorio
        # Normalizar ambas rutas para comparación
        assert os.path.normpath(result) == os.path.normpath(temp_dir)
    
    def test_cleanup_old_files_removes_old_files(self, temp_dir):
        """Verificar que cleanup_old_files elimina archivos antiguos"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear un archivo antiguo (modificar su timestamp)
        old_file = os.path.join(temp_dir, "old_file.pdf")
        with open(old_file, 'w') as f:
            f.write("old content")
        
        # Establecer timestamp antiguo (2 horas atrás)
        old_time = time.time() - (2 * 3600)
        os.utime(old_file, (old_time, old_time))
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # Verificar que el archivo fue eliminado
        assert not os.path.exists(old_file)
    
    def test_cleanup_old_files_keeps_recent_files(self, temp_dir):
        """Verificar que cleanup_old_files mantiene archivos recientes"""
        file_service = FileService(temp_dir, cleanup_hours=24)
        
        # Crear un archivo reciente
        recent_file = os.path.join(temp_dir, "recent_file.pdf")
        with open(recent_file, 'w') as f:
            f.write("recent content")
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # Verificar que el archivo NO fue eliminado
        assert os.path.exists(recent_file)
    
    def test_cleanup_old_files_mixed_ages(self, temp_dir):
        """Verificar que cleanup_old_files maneja archivos de diferentes edades"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear archivo antiguo
        old_file = os.path.join(temp_dir, "old_file.pdf")
        with open(old_file, 'w') as f:
            f.write("old content")
        old_time = time.time() - (2 * 3600)
        os.utime(old_file, (old_time, old_time))
        
        # Crear archivo reciente
        recent_file = os.path.join(temp_dir, "recent_file.pdf")
        with open(recent_file, 'w') as f:
            f.write("recent content")
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # Verificar resultados
        assert not os.path.exists(old_file)
        assert os.path.exists(recent_file)
    
    def test_cleanup_old_files_with_empty_directory(self, temp_dir):
        """Caso edge: directorio vacío no causa errores"""
        file_service = FileService(temp_dir)
        
        # No debe lanzar excepción
        file_service.cleanup_old_files()
        
        assert os.path.exists(temp_dir)
    
    def test_cleanup_old_files_ignores_subdirectories(self, temp_dir):
        """Verificar que cleanup_old_files ignora subdirectorios"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear un subdirectorio antiguo
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        old_time = time.time() - (2 * 3600)
        os.utime(subdir, (old_time, old_time))
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # Verificar que el subdirectorio NO fue eliminado
        assert os.path.exists(subdir)
    
    def test_cleanup_old_files_handles_permission_errors(self, temp_dir):
        """Verificar que cleanup_old_files maneja errores de permisos sin crashear"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear archivo antiguo
        old_file = os.path.join(temp_dir, "old_file.pdf")
        with open(old_file, 'w') as f:
            f.write("old content")
        old_time = time.time() - (2 * 3600)
        os.utime(old_file, (old_time, old_time))
        
        # Hacer el archivo de solo lectura (simular error de permisos en algunos sistemas)
        # Nota: esto puede no funcionar en todos los sistemas operativos
        try:
            os.chmod(old_file, 0o444)
            
            # Ejecutar limpieza - no debe crashear
            file_service.cleanup_old_files()
            
            # Restaurar permisos para limpieza
            os.chmod(old_file, 0o644)
        except Exception:
            # Si no podemos cambiar permisos, simplemente verificamos que no crashea
            file_service.cleanup_old_files()
    
    def test_cleanup_old_files_at_exact_threshold(self, temp_dir):
        """Caso edge: archivo exactamente en el umbral de tiempo"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear archivo exactamente en el umbral (1 hora atrás)
        threshold_file = os.path.join(temp_dir, "threshold_file.pdf")
        with open(threshold_file, 'w') as f:
            f.write("threshold content")
        threshold_time = time.time() - (1 * 3600)
        os.utime(threshold_file, (threshold_time, threshold_time))
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # El archivo en el umbral exacto debería ser eliminado (< cutoff)
        assert not os.path.exists(threshold_file)
    
    def test_multiple_files_cleanup(self, temp_dir):
        """Verificar limpieza de múltiples archivos antiguos"""
        file_service = FileService(temp_dir, cleanup_hours=1)
        
        # Crear múltiples archivos antiguos
        old_time = time.time() - (2 * 3600)
        for i in range(5):
            old_file = os.path.join(temp_dir, f"old_file_{i}.pdf")
            with open(old_file, 'w') as f:
                f.write(f"old content {i}")
            os.utime(old_file, (old_time, old_time))
        
        # Ejecutar limpieza
        file_service.cleanup_old_files()
        
        # Verificar que todos fueron eliminados
        for i in range(5):
            old_file = os.path.join(temp_dir, f"old_file_{i}.pdf")
            assert not os.path.exists(old_file)
    
    def test_storage_path_attribute(self, temp_dir):
        """Verificar que storage_path es accesible como atributo"""
        file_service = FileService(temp_dir)
        
        assert file_service.storage_path == temp_dir
    
    def test_cleanup_hours_attribute(self, temp_dir):
        """Verificar que cleanup_hours es accesible como atributo"""
        file_service = FileService(temp_dir, cleanup_hours=48)
        
        assert file_service.cleanup_hours == 48
