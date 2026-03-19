"""
Audio Campaign Service - Wrapper for audio generation functionality
Integrates the audio campaign generator with the main backend
"""
from pathlib import Path
from typing import Dict, Optional
import os
import shutil
from datetime import datetime, timedelta
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
        self.audio_files_path = Path("services/generador_audio_campaña/files")
        self.uploaded_event_audio_filename = "Gran Campaña - Hora y lugar del evento.mp3"
        
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
        Generates two separate files: one using the HOY logic, another for ESTE.
        
        Returns:
            Dictionary with processing results
            
        Raises:
            AudioProcessingError: If processing fails
        """
        logger.info("Starting dual campaign audio processing")
        
        target_hoy_path = str((self.temp_storage_path / "temp_evento_hoy.mp3").resolve())
        target_este_path = str((self.temp_storage_path / "temp_evento_este.mp3").resolve())

        # Process HOY version
        logger.info("Processing sequence for HOY version")
        processor_hoy = AudioProcessor(
            source_folder=self.audio_files_path,
            output_folder=self.temp_storage_path,
            event_audio_path=target_hoy_path
        )
        result_hoy = processor_hoy.process(version_suffix="_HOY")

        if not result_hoy.success:
            raise AudioProcessingError(f"Failed processing HOY: {result_hoy.error_message}")

        # Process ESTE version
        logger.info("Processing sequence for ESTE version")
        processor_este = AudioProcessor(
            source_folder=self.audio_files_path,
            output_folder=self.temp_storage_path,
            event_audio_path=target_este_path
        )
        result_este = processor_este.process(version_suffix="_ESTE")

        if not result_este.success:
            raise AudioProcessingError(f"Failed processing ESTE: {result_este.error_message}")
        
        return {
            "success": True,
            "output_files": [result_hoy.output_path.name, result_este.output_path.name],
            "duration_seconds": (result_hoy.final_duration_ms + result_este.final_duration_ms) / 2000,
            "warnings": result_hoy.validation_warnings + result_este.validation_warnings
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
    
    async def save_event_audios(self, file_hoy, file_este) -> list[str]:
        """
        Save uploaded event audio files to the temp storage directory.
        
        Args:
            file_hoy: UploadFile object for 'HOY' version
            file_este: UploadFile object for 'ESTE' version
            
        Returns:
            List of filenames of the saved files
            
        Raises:
            AudioProcessingError: If file saves fail
        """
        try:
            hoy_filename = "temp_evento_hoy.mp3"
            este_filename = "temp_evento_este.mp3"
            
            dest_hoy = self.temp_storage_path / hoy_filename
            dest_este = self.temp_storage_path / este_filename
            
            logger.info(f"Saving uploaded event HOY audio to: {dest_hoy}")
            with open(dest_hoy, "wb") as buffer:
                content = await file_hoy.read()
                buffer.write(content)
                
            logger.info(f"Saving uploaded event ESTE audio to: {dest_este}")
            with open(dest_este, "wb") as buffer:
                content = await file_este.read()
                buffer.write(content)
            
            logger.info("Event audios saved successfully")
            
            return [hoy_filename, este_filename]
            
        except Exception as e:
            error_msg = f"Failed to save event audio files: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def cleanup_old_event_audio(self):
        """
        Clean up old event audio files (older than 1 day).
        This is a placeholder for future implementation if needed.
        """
        # For now, we just replace the file each time
        # In the future, we could implement timestamp-based cleanup
        pass
