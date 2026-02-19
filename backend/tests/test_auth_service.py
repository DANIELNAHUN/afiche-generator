import pytest
from services.auth_service import AuthService


class TestAuthService:
    """Pruebas unitarias para AuthService"""
    
    def test_create_session_returns_unique_id(self):
        """Ejemplo específico de creación de sesión"""
        auth_service = AuthService()
        session_id, question = auth_service.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert question["number"] == 1
        assert "text" in question
        assert "answer" in question
    
    def test_create_session_generates_different_ids(self):
        """Verificar que múltiples sesiones tienen IDs diferentes"""
        auth_service = AuthService()
        session_id1, _ = auth_service.create_session()
        session_id2, _ = auth_service.create_session()
        
        assert session_id1 != session_id2
    
    def test_normalize_text_removes_punctuation(self):
        """Caso edge: texto con puntuación"""
        auth_service = AuthService()
        result = auth_service._normalize_text("¡Hola, Mundo!")
        assert result == "hola mundo"
    
    def test_normalize_text_removes_extra_spaces(self):
        """Caso edge: texto con espacios extras"""
        auth_service = AuthService()
        result = auth_service._normalize_text("  iglesia   central  ")
        assert result == "iglesia central"
    
    def test_normalize_text_converts_to_lowercase(self):
        """Verificar conversión a minúsculas"""
        auth_service = AuthService()
        result = auth_service._normalize_text("IGLESIA CENTRAL")
        assert result == "iglesia central"
    
    def test_normalize_text_handles_special_characters(self):
        """Caso edge: caracteres especiales"""
        auth_service = AuthService()
        result = auth_service._normalize_text("Iglesia@Central#123!")
        assert result == "iglesiacentral123"
    
    def test_validate_answer_with_invalid_session(self):
        """Condición de error: sesión inválida"""
        auth_service = AuthService()
        
        with pytest.raises(ValueError, match="Sesión inválida"):
            auth_service.validate_answer("invalid-id", 1, "answer")
    
    def test_validate_answer_correct_question_1(self):
        """Respuesta correcta en pregunta 1 avanza a pregunta 2"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        result = auth_service.validate_answer(session_id, 1, "iglesia central")
        
        assert result["success"] is True
        assert result["next_question"] == 2
        assert "question_text" in result
        assert auth_service.sessions[session_id].current_question == 2
    
    def test_validate_answer_correct_question_2(self):
        """Respuesta correcta en pregunta 2 avanza a pregunta 3"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        # Avanzar a pregunta 2
        auth_service.validate_answer(session_id, 1, "iglesia central")
        
        result = auth_service.validate_answer(session_id, 2, "lima")
        
        assert result["success"] is True
        assert result["next_question"] == 3
        assert auth_service.sessions[session_id].current_question == 3
    
    def test_validate_answer_correct_question_3_completes_auth(self):
        """Respuesta correcta en pregunta 3 completa autenticación"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        # Avanzar a pregunta 3
        auth_service.validate_answer(session_id, 1, "iglesia central")
        auth_service.validate_answer(session_id, 2, "lima")
        
        result = auth_service.validate_answer(session_id, 3, "esperanza viva")
        
        assert result["success"] is True
        assert result["message"] == "Autenticación exitosa"
        assert "next_question" not in result
        assert auth_service.sessions[session_id].authenticated is True
    
    def test_validate_answer_incorrect_resets_to_question_1(self):
        """Respuesta incorrecta reinicia a pregunta 1"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        # Avanzar a pregunta 2
        auth_service.validate_answer(session_id, 1, "iglesia central")
        
        # Responder incorrectamente pregunta 2
        result = auth_service.validate_answer(session_id, 2, "respuesta incorrecta")
        
        assert result["success"] is False
        assert result["next_question"] == 1
        assert "Reiniciando" in result["message"]
        assert auth_service.sessions[session_id].current_question == 1
    
    def test_validate_answer_normalizes_input(self):
        """Validación normaliza la entrada del usuario"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        # Responder con mayúsculas y espacios extras
        result = auth_service.validate_answer(session_id, 1, "  IGLESIA   CENTRAL  ")
        
        assert result["success"] is True
        assert result["next_question"] == 2
    
    def test_is_authenticated_returns_false_for_invalid_session(self):
        """is_authenticated retorna False para sesión inválida"""
        auth_service = AuthService()
        
        assert auth_service.is_authenticated("invalid-id") is False
    
    def test_is_authenticated_returns_false_for_unauthenticated_session(self):
        """is_authenticated retorna False para sesión no autenticada"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        assert auth_service.is_authenticated(session_id) is False
    
    def test_is_authenticated_returns_true_after_completion(self):
        """is_authenticated retorna True después de completar autenticación"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        # Completar autenticación
        auth_service.validate_answer(session_id, 1, "iglesia central")
        auth_service.validate_answer(session_id, 2, "lima")
        auth_service.validate_answer(session_id, 3, "esperanza viva")
        
        assert auth_service.is_authenticated(session_id) is True
    
    def test_session_data_stores_timestamp(self):
        """Verificar que SessionData almacena timestamp"""
        auth_service = AuthService()
        session_id, _ = auth_service.create_session()
        
        session_data = auth_service.sessions[session_id]
        assert session_data.created_at > 0
        assert isinstance(session_data.created_at, float)
