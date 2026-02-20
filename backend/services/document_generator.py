"""
Document Generator Service

Genera los 3 tipos de documentos PDF a partir de plantillas procesadas:
- PDF A4 vertical
- PDF 4x1 vertical
- Gigantografía 1x1.5m en CMYK
"""

import os
import subprocess
from typing import Dict, List
from PIL import Image
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


class DocumentGenerator:
    """
    Genera documentos PDF en diferentes formatos a partir de plantillas Word.
    
    Tipos de documentos:
    - a4: PDF en formato A4 vertical
    - 4x1: PDF en formato 4x1 vertical
    - gigantografia: PDF de 1x1.5 metros en modo CMYK para impresión profesional
    """
    
    def __init__(self, template_processor, temp_storage_path: str):
        """
        Inicializa el generador de documentos.
        
        Args:
            template_processor: Instancia de TemplateProcessor para procesar plantillas
            temp_storage_path: Ruta del directorio para almacenar archivos temporales
        """
        self.template_processor = template_processor
        self.temp_storage = temp_storage_path
        os.makedirs(temp_storage_path, exist_ok=True)
    
    def generate_all(self, data: Dict[str, str], project_name: str) -> List[Dict]:
        """
        Genera los 3 tipos de documentos PDF.
        
        Args:
            data: Diccionario con los datos del evento:
                - fecha_evento: Fecha del evento
                - hora_evento: Hora del evento
                - lugar_evento: Lugar del evento
                - referencia_evento: Referencia opcional
            project_name: Nombre del proyecto para nombrar los archivos
        
        Returns:
            Lista de diccionarios con información de cada documento generado:
            [
                {
                    "type": "a4",
                    "filename": "proyecto_a4.pdf",
                    "status": "success"
                },
                ...
            ]
        """
        results = []
        
        # 1. Generar A4
        try:
            a4_filename = self._generate_a4(data, project_name)
            results.append({
                "type": "a4",
                "filename": a4_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "a4",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        # 2. Generar 4x1
        try:
            format_4x1_filename = self._generate_4x1(data, project_name)
            results.append({
                "type": "4x1",
                "filename": format_4x1_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "4x1",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        # 3. Generar Gigantografía
        try:
            giga_filename = self._generate_gigantografia(data, project_name)
            results.append({
                "type": "gigantografia",
                "filename": giga_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "gigantografia",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        return results
    
    def _generate_a4(self, data: Dict[str, str], project_name: str) -> str:
        """
        Genera PDF en formato A4.
        
        Args:
            data: Datos del evento
            project_name: Nombre del proyecto
        
        Returns:
            Nombre del archivo generado
        """
        docx_path = os.path.join(self.temp_storage, f"{project_name}_a4.docx")
        pdf_path = os.path.join(self.temp_storage, f"{project_name}_a4.pdf")
        
        # Procesar plantilla
        self.template_processor.process_template("a4", data, docx_path)
        
        # Convertir a PDF usando LibreOffice
        self._convert_docx_to_pdf(docx_path, pdf_path)
        
        return f"{project_name}_a4.pdf"
    
    def _generate_4x1(self, data: Dict[str, str], project_name: str) -> str:
        """
        Genera PDF en formato 4x1.
        
        Args:
            data: Datos del evento
            project_name: Nombre del proyecto
        
        Returns:
            Nombre del archivo generado
        """
        docx_path = os.path.join(self.temp_storage, f"{project_name}_4x1.docx")
        pdf_path = os.path.join(self.temp_storage, f"{project_name}_4x1.pdf")
        
        # Procesar plantilla
        self.template_processor.process_template("4x1", data, docx_path)
        
        # Convertir a PDF
        self._convert_docx_to_pdf(docx_path, pdf_path)
        
        return f"{project_name}_4x1.pdf"
    
    def _generate_gigantografia(self, data: Dict[str, str], project_name: str) -> str:
        """
        Genera gigantografía 1x1.5m en CMYK.
        
        Proceso:
        1. Genera un documento A4 base
        2. Convierte el PDF a imagen
        3. Convierte la imagen a modo CMYK
        4. Redimensiona a 1x1.5 metros (100x150 cm) a 300 DPI
        5. Crea un nuevo PDF con la imagen redimensionada
        
        Args:
            data: Datos del evento
            project_name: Nombre del proyecto
        
        Returns:
            Nombre del archivo generado
        """
        # Primero generar el A4 base
        docx_path = os.path.join(self.temp_storage, f"{project_name}_giga_temp.docx")
        pdf_temp_path = os.path.join(self.temp_storage, f"{project_name}_giga_temp.pdf")
        pdf_final_path = os.path.join(self.temp_storage, f"{project_name}_gigantografia.pdf")
        
        # Procesar plantilla A4
        self.template_processor.process_template("a4", data, docx_path)
        self._convert_docx_to_pdf(docx_path, pdf_temp_path)
        
        # Convertir PDF a imagen
        images = convert_from_path(pdf_temp_path, dpi=300)
        img = images[0]
        
        # Convertir a CMYK
        if img.mode != 'CMYK':
            img = img.convert('CMYK')
        
        # Redimensionar a 1x1.5 metros (100x150 cm) a 300 DPI
        # 100cm = 39.37 inches, 150cm = 59.06 inches
        # A 300 DPI: 11811 x 17717 pixels
        target_size = (11811, 17717)
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Guardar como PDF usando reportlab
        c = canvas.Canvas(pdf_final_path, pagesize=(11811, 17717))
        
        # Guardar imagen temporalmente
        temp_img_path = os.path.join(self.temp_storage, f"{project_name}_temp.tiff")
        img_resized.save(temp_img_path, 'TIFF')
        
        # Dibujar en PDF
        c.drawImage(temp_img_path, 0, 0, width=11811, height=17717)
        c.save()
        
        # Limpiar archivos temporales
        os.remove(temp_img_path)
        os.remove(pdf_temp_path)
        os.remove(docx_path)
        
        return f"{project_name}_gigantografia.pdf"
    
    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str):
        """
        Convierte DOCX a PDF usando LibreOffice.
        
        Args:
            docx_path: Ruta del archivo DOCX
            pdf_path: Ruta donde guardar el PDF
        
        Raises:
            subprocess.CalledProcessError: Si LibreOffice falla
        """
        # Detectar el ejecutable de LibreOffice según el sistema operativo
        import platform
        system = platform.system()
        
        if system == "Windows":
            # Rutas comunes de LibreOffice en Windows
            possible_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            libreoffice_cmd = None
            for path in possible_paths:
                if os.path.exists(path):
                    libreoffice_cmd = path
                    break
            
            if not libreoffice_cmd:
                raise FileNotFoundError(
                    "LibreOffice no encontrado. Por favor instala LibreOffice desde https://www.libreoffice.org/"
                )
        else:
            # Linux/Mac
            libreoffice_cmd = "libreoffice"
        
        # Convertir rutas a absolutas para evitar problemas
        docx_path_abs = os.path.abspath(docx_path)
        output_dir_abs = os.path.abspath(os.path.dirname(pdf_path))
        
        # Comando para LibreOffice en modo headless
        cmd = [
            libreoffice_cmd,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir_abs,
            docx_path_abs
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # LibreOffice genera el PDF con el mismo nombre base en el directorio de salida
        base_name = os.path.basename(docx_path_abs).replace('.docx', '.pdf')
        generated_pdf = os.path.join(output_dir_abs, base_name)
        
        # Si el PDF generado tiene un nombre diferente al esperado, renombrarlo
        pdf_path_abs = os.path.abspath(pdf_path)
        if generated_pdf != pdf_path_abs and os.path.exists(generated_pdf):
            if os.path.exists(pdf_path_abs):
                os.remove(pdf_path_abs)
            os.rename(generated_pdf, pdf_path_abs)
