"""
Template Processor Service

Procesa plantillas Word (.docx) reemplazando marcadores con datos del evento.
"""

from docx import Document
from typing import Dict
import os


class TemplateProcessor:
    """
    Procesa plantillas Word reemplazando campos editables con datos del evento.
    
    Marcadores soportados:
    - {{fecha_evento}}: Fecha del evento
    - {{hora_evento}}: Hora del evento
    - {{lugar_evento}}: Lugar del evento
    - {{referencia_evento}}: Referencia opcional del evento
    """
    
    def __init__(self, template_dir: str = None):
        """
        Inicializa el procesador con la configuración de plantillas.
        
        Args:
            template_dir: Directorio donde se encuentran las plantillas.
                         Si es None, usa backend/templates/.
        """
        if template_dir is None:
            # Por defecto, las plantillas están en backend/templates/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            self.template_dir = os.path.join(backend_dir, "templates")
        else:
            self.template_dir = template_dir
        
        self.templates = {
            "a4": "Formato a4.docx",
            "4x1": "Formato 4x1.docx"
        }
    
    def process_template(self, template_type: str, data: Dict[str, str], output_path: str) -> str:
        """
        Procesa una plantilla Word reemplazando campos con datos.
        
        Args:
            template_type: Tipo de plantilla ("a4" o "4x1")
            data: Diccionario con los datos del evento:
                - fecha_evento: Fecha del evento (requerido)
                - hora_evento: Hora del evento (requerido)
                - lugar_evento: Lugar del evento (requerido)
                - referencia_evento: Referencia opcional (puede ser vacío)
            output_path: Ruta donde guardar el documento procesado
        
        Returns:
            Ruta del archivo procesado
            
        Raises:
            FileNotFoundError: Si la plantilla no existe
            KeyError: Si template_type no es válido
        """
        if template_type not in self.templates:
            raise KeyError(f"Tipo de plantilla inválido: {template_type}")
        
        template_path = os.path.join(self.template_dir, self.templates[template_type])
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
        
        # Cargar el documento
        doc = Document(template_path)
        
        # Reemplazar en párrafos
        for paragraph in doc.paragraphs:
            self._replace_in_runs(paragraph.runs, data)
        
        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_runs(paragraph.runs, data)
        
        # Guardar el documento procesado
        doc.save(output_path)
        return output_path
    
    def _replace_in_runs(self, runs, data: Dict[str, str]):
        """
        Reemplaza marcadores en runs de texto.
        
        Los marcadores tienen el formato {{nombre_campo}} y son reemplazados
        con los valores correspondientes del diccionario data.
        
        Args:
            runs: Lista de runs de texto de un párrafo
            data: Diccionario con los valores de reemplazo
        """
        # Definir los marcadores y sus reemplazos
        replacements = {
            "{{fecha_evento}}": data.get("fecha_evento", ""),
            "{{hora_evento}}": data.get("hora_evento", ""),
            "{{lugar_evento}}": data.get("lugar_evento", ""),
            "{{referencia_evento}}": data.get("referencia_evento", "")
        }
        
        # Reemplazar en cada run
        for run in runs:
            for marker, value in replacements.items():
                if marker in run.text:
                    run.text = run.text.replace(marker, value)
