"""
Unit tests for DocumentGenerator service
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from services.document_generator import DocumentGenerator


@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para las pruebas"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_template_processor():
    """Mock del TemplateProcessor"""
    processor = Mock()
    processor.process_template = Mock(return_value="/fake/path/output.docx")
    return processor


@pytest.fixture
def document_generator(mock_template_processor, temp_dir):
    """Crea una instancia de DocumentGenerator para pruebas"""
    return DocumentGenerator(mock_template_processor, temp_dir)


@pytest.fixture
def event_data():
    """Datos de evento de ejemplo"""
    return {
        "fecha_evento": "15 de Diciembre, 2024",
        "hora_evento": "7:00 PM",
        "lugar_evento": "Auditorio Central",
        "referencia_evento": "Juan 3:16"
    }


class TestDocumentGenerator:
    """Tests para la clase DocumentGenerator"""
    
    def test_init_creates_temp_storage(self, mock_template_processor, temp_dir):
        """Verifica que el constructor crea el directorio de almacenamiento temporal"""
        storage_path = os.path.join(temp_dir, "test_storage")
        generator = DocumentGenerator(mock_template_processor, storage_path)
        
        assert os.path.exists(storage_path)
        assert generator.temp_storage == storage_path
        assert generator.template_processor == mock_template_processor
    
    def test_generate_all_returns_three_documents(self, document_generator, event_data):
        """Verifica que generate_all intenta generar 3 documentos"""
        with patch.object(document_generator, '_generate_a4', return_value="test_a4.pdf"), \
             patch.object(document_generator, '_generate_4x1', return_value="test_4x1.pdf"), \
             patch.object(document_generator, '_generate_gigantografia', return_value="test_giga.pdf"):
            
            results = document_generator.generate_all(event_data, "test_project")
            
            assert len(results) == 3
            assert results[0]["type"] == "a4"
            assert results[1]["type"] == "4x1"
            assert results[2]["type"] == "gigantografia"
    
    def test_generate_all_handles_individual_errors(self, document_generator, event_data):
        """Verifica que errores individuales no fallan toda la operación"""
        with patch.object(document_generator, '_generate_a4', side_effect=Exception("A4 error")), \
             patch.object(document_generator, '_generate_4x1', return_value="test_4x1.pdf"), \
             patch.object(document_generator, '_generate_gigantografia', return_value="test_giga.pdf"):
            
            results = document_generator.generate_all(event_data, "test_project")
            
            assert len(results) == 3
            assert results[0]["status"] == "error"
            assert results[0]["message"] == "A4 error"
            assert results[1]["status"] == "success"
            assert results[2]["status"] == "success"
    
    def test_generate_a4_calls_template_processor(self, document_generator, event_data, mock_template_processor):
        """Verifica que _generate_a4 llama al template processor correctamente"""
        with patch.object(document_generator, '_convert_docx_to_pdf'):
            filename = document_generator._generate_a4(event_data, "test_project")
            
            # Verificar que se llamó al template processor
            mock_template_processor.process_template.assert_called_once()
            call_args = mock_template_processor.process_template.call_args
            assert call_args[0][0] == "a4"
            assert call_args[0][1] == event_data
            
            # Verificar el nombre del archivo retornado
            assert filename == "test_project_a4.pdf"
    
    def test_generate_4x1_calls_template_processor(self, document_generator, event_data, mock_template_processor):
        """Verifica que _generate_4x1 llama al template processor correctamente"""
        with patch.object(document_generator, '_convert_docx_to_pdf'):
            filename = document_generator._generate_4x1(event_data, "test_project")
            
            # Verificar que se llamó al template processor
            mock_template_processor.process_template.assert_called_once()
            call_args = mock_template_processor.process_template.call_args
            assert call_args[0][0] == "4x1"
            assert call_args[0][1] == event_data
            
            # Verificar el nombre del archivo retornado
            assert filename == "test_project_4x1.pdf"
    
    def test_generate_gigantografia_converts_to_cmyk(self, document_generator, event_data, mock_template_processor):
        """Verifica que _generate_gigantografia convierte a CMYK"""
        # Mock de PIL Image
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_cmyk_image = MagicMock()
        mock_cmyk_image.mode = 'CMYK'
        mock_image.convert.return_value = mock_cmyk_image
        mock_resized_image = MagicMock()
        mock_cmyk_image.resize.return_value = mock_resized_image
        
        with patch.object(document_generator, '_convert_docx_to_pdf'), \
             patch('services.document_generator.convert_from_path', return_value=[mock_image]), \
             patch('services.document_generator.canvas.Canvas') as mock_canvas, \
             patch('os.remove'):
            
            filename = document_generator._generate_gigantografia(event_data, "test_project")
            
            # Verificar que se convirtió a CMYK
            mock_image.convert.assert_called_once_with('CMYK')
            
            # Verificar que se redimensionó a las dimensiones correctas (11811 x 17717)
            assert mock_cmyk_image.resize.called
            call_args = mock_cmyk_image.resize.call_args[0]
            assert call_args[0] == (11811, 17717)
            
            # Verificar el nombre del archivo retornado
            assert filename == "test_project_gigantografia.pdf"
    
    def test_convert_docx_to_pdf_calls_libreoffice(self, document_generator, temp_dir):
        """Verifica que _convert_docx_to_pdf llama a LibreOffice correctamente"""
        docx_path = os.path.join(temp_dir, "test.docx")
        pdf_path = os.path.join(temp_dir, "test.pdf")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Crear archivo temporal para simular la salida de LibreOffice
            with open(docx_path.replace('.docx', '.pdf'), 'w') as f:
                f.write("fake pdf")
            
            document_generator._convert_docx_to_pdf(docx_path, pdf_path)
            
            # Verificar que se llamó a subprocess.run con los argumentos correctos
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert 'libreoffice' in call_args
            assert '--headless' in call_args
            assert '--convert-to' in call_args
            assert 'pdf' in call_args
    
    def test_filename_convention(self, document_generator, event_data):
        """Verifica que los nombres de archivo siguen la convención {nombre_proyecto}_{tipo}.pdf"""
        with patch.object(document_generator, '_convert_docx_to_pdf'), \
             patch('services.document_generator.convert_from_path'), \
             patch('services.document_generator.canvas.Canvas'), \
             patch('os.remove'):
            
            # Mock para gigantografía
            mock_image = MagicMock()
            mock_image.mode = 'CMYK'
            mock_image.resize.return_value = mock_image
            
            with patch('services.document_generator.convert_from_path', return_value=[mock_image]):
                a4_filename = document_generator._generate_a4(event_data, "mi_proyecto")
                format_4x1_filename = document_generator._generate_4x1(event_data, "mi_proyecto")
                giga_filename = document_generator._generate_gigantografia(event_data, "mi_proyecto")
                
                assert a4_filename == "mi_proyecto_a4.pdf"
                assert format_4x1_filename == "mi_proyecto_4x1.pdf"
                assert giga_filename == "mi_proyecto_gigantografia.pdf"
