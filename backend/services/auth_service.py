import uuid
import re
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class SessionData:
    """Representa el estado de una sesión de usuario"""
    session_id: str
    current_question: int  # 1, 2, o 3
    authenticated: bool
    created_at: float  # timestamp


class AuthService:
    """Servicio de autenticación con gestión de sesiones"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        # Cargar preguntas y respuestas dinámicamente desde variables de entorno
        self.security_questions = self._load_security_questions()
        self.total_questions = len(self.security_questions)
    
    def _load_security_questions(self) -> list:
        """
        Carga todas las preguntas de seguridad desde variables de entorno
        Busca pares SECURITY_QUESTION_N y SECURITY_ANSWER_N donde N es un número
        
        Returns:
            Lista de diccionarios con preguntas y respuestas
        """
        questions = []
        i = 1
        
        while True:
            question_key = f"SECURITY_QUESTION_{i}"
            answer_key = f"SECURITY_ANSWER_{i}"
            
            question_text = os.getenv(question_key)
            answer_text = os.getenv(answer_key)
            
            # Si no existe la pregunta o respuesta, terminamos
            if not question_text or not answer_text:
                break
            
            questions.append({
                "number": i,
                "text": question_text,
                "answer": answer_text
            })
            i += 1
        
        # Si no hay preguntas configuradas, usar valores por defecto
        if not questions:
            questions = [
                {
                    "number": 1,
                    "text": "¿Cuál es el nombre de tu iglesia?",
                    "answer": "iglesia central"
                }
            ]
        
        return questions
    
    def create_session(self) -> Tuple[str, dict]:
        """
        Genera un nuevo Session_ID y retorna la primera pregunta
        
        Returns:
            Tuple con (session_id, primera_pregunta)
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionData(
            session_id=session_id,
            current_question=1,
            authenticated=False,
            created_at=time.time()
        )
        return session_id, self.security_questions[0]
    
    def validate_answer(self, session_id: str, question_number: int, answer: str) -> dict:
        """
        Valida una respuesta y retorna el resultado
        
        Args:
            session_id: ID de la sesión
            question_number: Número de pregunta (1 a N)
            answer: Respuesta del usuario
            
        Returns:
            Diccionario con resultado de validación
            
        Raises:
            ValueError: Si la sesión es inválida
        """
        if session_id not in self.sessions:
            raise ValueError("Sesión inválida")
        
        normalized_answer = self._normalize_text(answer)
        expected_answer = self.security_questions[question_number - 1]["answer"]
        normalized_expected_answer = self._normalize_text(expected_answer)
        
        if normalized_answer == normalized_expected_answer:
            if question_number == self.total_questions:
                # Autenticación completa - última pregunta respondida correctamente
                self.sessions[session_id].authenticated = True
                return {"success": True, "message": "Autenticación exitosa"}
            else:
                # Avanzar a siguiente pregunta
                self.sessions[session_id].current_question = question_number + 1
                next_q = self.security_questions[question_number]
                return {
                    "success": True,
                    "next_question": next_q["number"],
                    "question_text": next_q["text"]
                }
        else:
            # Reiniciar a pregunta 1
            self.sessions[session_id].current_question = 1
            return {
                "success": False,
                "message": "Respuesta incorrecta. Reiniciando...",
                "next_question": 1,
                "question_text": self.security_questions[0]["text"]
            }
    
    def is_authenticated(self, session_id: str) -> bool:
        """
        Verifica si una sesión está autenticada
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            True si la sesión existe y está autenticada, False en caso contrario
        """
        return session_id in self.sessions and self.sessions[session_id].authenticated
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto: lowercase, trim, remover puntuación extra
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        # Convertir a minúsculas y eliminar espacios al inicio/final
        text = text.strip().lower()
        # Remover puntuación
        text = re.sub(r'[^\w\s]', '', text)
        # Normalizar espacios múltiples a uno solo
        text = re.sub(r'\s+', ' ', text)
        return text
