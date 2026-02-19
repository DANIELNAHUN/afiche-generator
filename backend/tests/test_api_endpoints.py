"""
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, auth_service, file_service
import tempfile


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_root_endpoint_returns_200(self):
        """Test that root endpoint returns 200 status"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "running"


class TestAuthEndpoints:
    """Tests for authentication endpoints"""
    
    def test_start_session_returns_session_id(self):
        """Test that start-session returns a session ID and first question"""
        client = TestClient(app)
        response = client.post("/api/auth/start-session")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["question_number"] == 1
        assert "question_text" in data
        assert len(data["session_id"]) > 0
    
    def test_validate_answer_with_invalid_session_returns_401(self):
        """Test that validating with invalid session returns 401"""
        client = TestClient(app)
        response = client.post("/api/auth/validate-answer", json={
            "session_id": "invalid-session-id",
            "question_number": 1,
            "answer": "test"
        })
        assert response.status_code == 401
    
    def test_validate_answer_with_correct_answer_progresses(self):
        """Test that correct answer progresses to next question"""
        client = TestClient(app)
        # Start session
        session_response = client.post("/api/auth/start-session")
        session_id = session_response.json()["session_id"]
        
        # Answer first question correctly
        response = client.post("/api/auth/validate-answer", json={
            "session_id": session_id,
            "question_number": 1,
            "answer": "iglesia central"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["next_question"] == 2
    
    def test_validate_answer_with_incorrect_answer_resets(self):
        """Test that incorrect answer resets to question 1"""
        client = TestClient(app)
        # Start session
        session_response = client.post("/api/auth/start-session")
        session_id = session_response.json()["session_id"]
        
        # Answer first question incorrectly
        response = client.post("/api/auth/validate-answer", json={
            "session_id": session_id,
            "question_number": 1,
            "answer": "wrong answer"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["next_question"] == 1
        assert "Respuesta incorrecta" in data["message"]


class TestGenerateEndpoint:
    """Tests for document generation endpoint"""
    
    def test_generate_without_authentication_returns_401(self):
        """Test that generation without authentication returns 401"""
        client = TestClient(app)
        response = client.post("/api/generate", json={
            "session_id": "invalid-session",
            "fecha_evento": "15 de Diciembre",
            "hora_evento": "7:00 PM",
            "lugar_evento": "Auditorio Central",
            "referencia_evento": "",
            "nombre_proyecto": "test_project"
        })
        assert response.status_code == 401
    
    def test_generate_with_empty_required_field_returns_422(self):
        """Test that generation with empty required field returns validation error"""
        client = TestClient(app)
        # Start and authenticate session
        session_response = client.post("/api/auth/start-session")
        session_id = session_response.json()["session_id"]
        
        # Authenticate
        for i, answer in enumerate(["iglesia central", "lima", "esperanza viva"], 1):
            client.post("/api/auth/validate-answer", json={
                "session_id": session_id,
                "question_number": i,
                "answer": answer
            })
        
        # Try to generate with empty fecha_evento
        response = client.post("/api/generate", json={
            "session_id": session_id,
            "fecha_evento": "",
            "hora_evento": "7:00 PM",
            "lugar_evento": "Auditorio Central",
            "referencia_evento": "",
            "nombre_proyecto": "test_project"
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_generate_returns_json_response(self):
        """Test that generate endpoint returns JSON response"""
        client = TestClient(app)
        # Start and authenticate session
        session_response = client.post("/api/auth/start-session")
        session_id = session_response.json()["session_id"]
        
        # Authenticate
        for i, answer in enumerate(["iglesia central", "lima", "esperanza viva"], 1):
            client.post("/api/auth/validate-answer", json={
                "session_id": session_id,
                "question_number": i,
                "answer": answer
            })
        
        # Generate documents
        response = client.post("/api/generate", json={
            "session_id": session_id,
            "fecha_evento": "15 de Diciembre",
            "hora_evento": "7:00 PM",
            "lugar_evento": "Auditorio Central",
            "referencia_evento": "Juan 3:16",
            "nombre_proyecto": "test_project"
        })
        
        # Verify response format
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "success" in data
        assert "documents" in data


class TestDownloadEndpoint:
    """Tests for file download endpoint"""
    
    def test_download_nonexistent_file_returns_404(self):
        """Test that downloading nonexistent file returns 404"""
        client = TestClient(app)
        response = client.get("/api/download/nonexistent_file.pdf")
        assert response.status_code == 404
    
    def test_download_existing_file_returns_pdf(self):
        """Test that downloading existing file returns PDF with correct content type"""
        client = TestClient(app)
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.pdf',
            dir=file_service.storage_path,
            delete=False
        ) as f:
            f.write("test content")
            filename = os.path.basename(f.name)
        
        try:
            response = client.get(f"/api/download/{filename}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
        finally:
            # Cleanup
            os.remove(os.path.join(file_service.storage_path, filename))


class TestIntegrationFlow:
    """Integration tests for complete user flow"""
    
    def test_complete_authentication_and_generation_flow(self):
        """Test complete flow from authentication to generation"""
        client = TestClient(app)
        # 1. Start session
        session_response = client.post("/api/auth/start-session")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # 2. Answer all questions correctly
        questions_answers = [
            (1, "iglesia central"),
            (2, "lima"),
            (3, "esperanza viva")
        ]
        
        for q_num, answer in questions_answers:
            response = client.post("/api/auth/validate-answer", json={
                "session_id": session_id,
                "question_number": q_num,
                "answer": answer
            })
            assert response.status_code == 200
            assert response.json()["success"] is True
        
        # 3. Verify session is authenticated
        assert auth_service.is_authenticated(session_id)
        
        # 4. Generate documents
        response = client.post("/api/generate", json={
            "session_id": session_id,
            "fecha_evento": "15 de Diciembre, 2024",
            "hora_evento": "7:00 PM",
            "lugar_evento": "Auditorio Central",
            "referencia_evento": "Juan 3:16",
            "nombre_proyecto": "integration_test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["documents"]) == 3
        
        # Verify document types
        doc_types = [doc["type"] for doc in data["documents"]]
        assert "a4" in doc_types
        assert "4x1" in doc_types
        assert "gigantografia" in doc_types
