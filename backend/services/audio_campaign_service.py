"""
Audio Campaign Service - Wrapper for audio generation functionality
Integrates the audio campaign generator with the main backend
"""
from pathlib import Path
from typing import Dict, Optional
import os
from dotenv import load_dotenv

import sys
from pathlib import Path

# Add the generador_audio_campaña directory to Python path
_generator_path = Path(__file__).parent / "generador_audio_campaña"
if str(_generator_path) not in sys.path:
    sys.path.insert(0, str(_generator_path))

from src.audio_processor import AudioProcessor
from src.elevenlabs_generator import ElevenLabsGenerator, CampaignParams
from src.exceptions import AudioProcessingError
from src.logger_config import get_logger

load_dotenv()

logger = get_logger('audio_campaign_service')


class AudioCampaignService:
    """Service for generating campaign audio files."""
    
    def __init__(self, temp_storage_path: str):
        """
        Initialize the audio campaign service.
        
        Args:
            temp_storage_path: Path to temporary storage folder
        """
        self.temp_storage_path = Path(temp_storage_path)
        self.audio_files_path = Path("backend/services/generador_audio_campaña/files")
        
        # Get ElevenLabs credentials from environment
        self.api_key = os.getenv('ELEVEN_API_KEY')
        self.voice_id = os.getenv('ELEVEN_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')
        
        logger.info(f"AudioCampaignService initialized")
        logger.info(f"Temp storage: {self.temp_storage_path}")
        logger.info(f"Audio files: {self.audio_files_path}")
    
    def generate_tts_audio(
        self,
        fecha: str,
        hora: str,
        lugar: str,
        referencia: str,
        version: str = "both"
    ) -> Dict[str, str]:
        """
        Generate text-to-speech audio for campaign announcement.
        
        Args:
            fecha: Event date (e.g., "DOMINGO 15 DE MARZO")
            hora: Event time (e.g., "5:30 PM")
            lugar: Event location (e.g., "PLAZA DE LA BANDERA")
            referencia: Location reference (e.g., "CERCA AL OVALO")
            version: Version to generate ("este", "hoy", or "both")
            
        Returns:
            Dictionary with generated file paths
            
        Raises:
            AudioProcessingError: If API key is missing or generation fails
        """
        if not self.api_key:
            raise AudioProcessingError(
                "ELEVEN_API_KEY not configured. Please set it in .env file"
            )
        
        logger.info(f"Generating TTS audio - version: {version}")
        
        # Create campaign parameters
        params = CampaignParams(
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            referencia=referencia
        )
        
        # Initialize generator
        generator = ElevenLabsGenerator(self.api_key, self.voice_id)
        
        # Generate audio based on version
        results = {}
        
        if version == "both":
            paths = generator.generate_both_versions(
                params, 
                self.temp_storage_path
            )
            results['este'] = str(paths['este'])
            results['hoy'] = str(paths['hoy'])
        else:
            use_today = version == "hoy"
            path = generator.generate_campaign_audio(
                params,
                self.temp_storage_path,
                use_today=use_today
            )
            results[version] = str(path)
        
        logger.info(f"TTS audio generated successfully: {results}")
        return results
    
    def process_campaign_audio(self) -> Dict[str, any]:
        """
        Process campaign audio by combining locutor files with background music.
        
        Returns:
            Dictionary with processing results
            
        Raises:
            AudioProcessingError: If processing fails
        """
        logger.info("Starting campaign audio processing")
        
        # Initialize audio processor
        processor = AudioProcessor(
            source_folder=self.audio_files_path,
            output_folder=self.temp_storage_path
        )
        
        # Process audio
        result = processor.process()
        
        if not result.success:
            raise AudioProcessingError(result.error_message)
        
        return {
            "success": True,
            "output_file": str(result.output_path),
            "duration_seconds": result.final_duration_ms / 1000,
            "warnings": result.validation_warnings
        }
    
    def test_elevenlabs_connection(self) -> bool:
        """
        Test connection to ElevenLabs API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.api_key:
            logger.warning("Cannot test connection: ELEVEN_API_KEY not configured")
            return False
        
        generator = ElevenLabsGenerator(self.api_key, self.voice_id)
        return generator.test_connection()
