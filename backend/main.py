"""
FastAPI application for Generador de Recursos Evangelísticos
Main entry point for the backend API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from services.auth_service import AuthService
from services.template_processor import TemplateProcessor
from services.document_generator import DocumentGenerator
from services.file_service import FileService

# Create FastAPI app
app = FastAPI(
    title="Generador de Recursos Evangelísticos API",
    description="API para generación automática de recursos publicitarios evangelísticos",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_service = AuthService()
template_processor = TemplateProcessor()
temp_storage_path = os.getenv("TEMP_STORAGE_PATH", "./temp_files")
document_generator = DocumentGenerator(template_processor, temp_storage_path)
file_service = FileService(temp_storage_path)


# Pydantic Models
class SessionResponse(BaseModel):
    """Response for session creation"""
    session_id: str
    question_number: int
    question_text: str
    total_questions: int


class ValidateAnswerRequest(BaseModel):
    """Request for answer validation"""
    session_id: str
    question_number: int
    answer: str


class ValidationResponse(BaseModel):
    """Response for answer validation"""
    success: bool
    message: Optional[str] = None
    next_question: Optional[int] = None
    question_text: Optional[str] = None


class GenerateRequest(BaseModel):
    """Request for document generation"""
    session_id: str
    fecha_evento: str = Field(..., min_length=1)
    hora_evento: str = Field(..., min_length=1)
    lugar_evento: str = Field(..., min_length=1)
    referencia_evento: Optional[str] = ""
    nombre_proyecto: str = Field(..., min_length=1)


class DocumentInfo(BaseModel):
    """Information about a generated document"""
    type: str
    filename: str
    status: str
    message: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response for document generation"""
    success: bool
    documents: List[DocumentInfo]


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Generador de Recursos Evangelísticos API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/auth/start-session", response_model=SessionResponse)
async def start_session():
    """
    Start a new authentication session
    Returns a session ID and the first security question
    """
    try:
        session_id, question = auth_service.create_session()
        return SessionResponse(
            session_id=session_id,
            question_number=question["number"],
            question_text=question["text"],
            total_questions=auth_service.total_questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar sesión: {str(e)}")


@app.post("/api/auth/validate-answer", response_model=ValidationResponse)
async def validate_answer(request: ValidateAnswerRequest):
    """
    Validate an answer to a security question
    Returns validation result and next question if applicable
    """
    try:
        result = auth_service.validate_answer(
            request.session_id,
            request.question_number,
            request.answer
        )
        return ValidationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar respuesta: {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_documents(request: GenerateRequest):
    """
    Generate PDF documents for an event
    Requires authenticated session
    """
    # Verify authentication
    if not auth_service.is_authenticated(request.session_id):
        raise HTTPException(status_code=401, detail="Sesión no autenticada")
    
    # Validate required fields
    if not request.nombre_proyecto.strip():
        raise HTTPException(status_code=400, detail="nombre_proyecto no puede estar vacío")
    
    try:
        # Prepare event data
        event_data = {
            "fecha_evento": request.fecha_evento,
            "hora_evento": request.hora_evento,
            "lugar_evento": request.lugar_evento,
            "referencia_evento": request.referencia_evento or ""
        }
        
        # Generate documents
        results = document_generator.generate_all(event_data, request.nombre_proyecto)
        
        # Convert results to DocumentInfo objects
        documents = [DocumentInfo(**doc) for doc in results]
        
        return GenerateResponse(success=True, documents=documents)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Plantilla no encontrada: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando documentos: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download a generated PDF file
    Returns the file as a response
    """
    file_path = file_service.get_file_path(filename)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar archivo: {str(e)}")
