"""
Audio Campaign Endpoints
Separate module for audio generation endpoints
"""
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict

from services.audio_campaign_service import AudioCampaignService
from services.generador_audio_campaña.src.exceptions import AudioProcessingError


# Pydantic Models
class GenerateTTSRequest(BaseModel):
    """Request for TTS audio generation"""
    session_id: str
    fecha: str = Field(..., min_length=1, description="Event date (e.g., 'DOMINGO 15 DE MARZO')")
    hora: str = Field(..., min_length=1, description="Event time (e.g., '5:30 PM')")
    lugar: str = Field(..., min_length=1, description="Event location")
    referencia: str = Field(default="", description="Location reference")
    version: str = Field(default="both", description="Version: 'este', 'hoy', or 'both'")


class TTSResponse(BaseModel):
    """Response for TTS generation"""
    success: bool
    files: Dict[str, str]
    message: Optional[str] = None


class ProcessAudioRequest(BaseModel):
    """Request for audio processing"""
    session_id: str


class ProcessAudioResponse(BaseModel):
    """Response for audio processing"""
    success: bool
    output_file: str
    duration_seconds: float
    warnings: list


def register_audio_endpoints(app, auth_service, audio_campaign_service: AudioCampaignService):
    """Register audio campaign endpoints to the FastAPI app."""
    
    @app.post("/api/audio/generate-tts", response_model=TTSResponse)
    async def generate_tts_audio(request: GenerateTTSRequest):
        """
        Generate text-to-speech audio for campaign announcement using ElevenLabs.
        Requires authenticated session.
        """
        # Verify authentication
        if not auth_service.is_authenticated(request.session_id):
            raise HTTPException(status_code=401, detail="Sesión no autenticada")
        
        # Validate version parameter
        if request.version not in ["este", "hoy", "both"]:
            raise HTTPException(
                status_code=400, 
                detail="version debe ser 'este', 'hoy' o 'both'"
            )
        
        try:
            files = audio_campaign_service.generate_tts_audio(
                fecha=request.fecha,
                hora=request.hora,
                lugar=request.lugar,
                referencia=request.referencia,
                version=request.version
            )
            
            return TTSResponse(
                success=True,
                files=files,
                message="Audio TTS generado exitosamente"
            )
        except AudioProcessingError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generando audio TTS: {str(e)}"
            )
    
    @app.post("/api/audio/process-campaign", response_model=ProcessAudioResponse)
    async def process_campaign_audio(request: ProcessAudioRequest):
        """
        Process campaign audio by combining locutor files with background music.
        Requires authenticated session.
        """
        # Verify authentication
        if not auth_service.is_authenticated(request.session_id):
            raise HTTPException(status_code=401, detail="Sesión no autenticada")
        
        try:
            result = audio_campaign_service.process_campaign_audio()
            
            return ProcessAudioResponse(
                success=result["success"],
                output_file=result["output_file"],
                duration_seconds=result["duration_seconds"],
                warnings=result["warnings"]
            )
        except AudioProcessingError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando audio de campaña: {str(e)}"
            )
    
    @app.get("/api/audio/test-connection")
    async def test_elevenlabs_connection():
        """
        Test connection to ElevenLabs API.
        Does not require authentication.
        """
        try:
            is_connected = audio_campaign_service.test_elevenlabs_connection()
            
            if is_connected:
                return {
                    "success": True,
                    "message": "Conexión exitosa con ElevenLabs API"
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo conectar con ElevenLabs API"
                }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error probando conexión: {str(e)}"
            )
