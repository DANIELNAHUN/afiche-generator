#!/usr/bin/env python3
"""
Integration test for the Generador de Recursos Evangelísticos
Tests the complete flow from authentication to document generation
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test that the API is running"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "running"
    print("✓ Health endpoint working")
    return True

def test_authentication_flow():
    """Test the complete authentication flow"""
    print("\nTesting authentication flow...")
    
    # Step 1: Start session
    print("  1. Starting session...")
    response = requests.post(f"{BASE_URL}/api/auth/start-session")
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]
    assert "session_id" in data
    assert "question_number" in data
    assert data["question_number"] == 1
    print(f"  ✓ Session started: {session_id}")
    print(f"    Question 1: {data['question_text']}")
    
    # Step 2: Answer question 1 correctly
    print("  2. Answering question 1...")
    response = requests.post(f"{BASE_URL}/api/auth/validate-answer", json={
        "session_id": session_id,
        "question_number": 1,
        "answer": "iglesia central"  # Correct answer (will be normalized)
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["next_question"] == 2
    print(f"  ✓ Question 1 answered correctly")
    print(f"    Question 2: {data['question_text']}")
    
    # Step 3: Answer question 2 correctly
    print("  3. Answering question 2...")
    response = requests.post(f"{BASE_URL}/api/auth/validate-answer", json={
        "session_id": session_id,
        "question_number": 2,
        "answer": "lima"  # Correct answer
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["next_question"] == 3
    print(f"  ✓ Question 2 answered correctly")
    print(f"    Question 3: {data['question_text']}")
    
    # Step 4: Answer question 3 correctly
    print("  4. Answering question 3...")
    response = requests.post(f"{BASE_URL}/api/auth/validate-answer", json={
        "session_id": session_id,
        "question_number": 3,
        "answer": "esperanza viva"  # Correct answer
    })
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"    Response: {data}")
    assert data["success"] == True, f"Expected success=True, got {data}"
    # No next_question when authentication is complete
    print(f"  ✓ Question 3 answered correctly - Authentication complete!")
    
    return session_id

def test_unauthenticated_generation():
    """Test that generation fails without authentication"""
    print("\nTesting unauthenticated generation...")
    response = requests.post(f"{BASE_URL}/api/generate", json={
        "session_id": "invalid-session-id",
        "fecha_evento": "15 de Diciembre, 2024",
        "hora_evento": "7:00 PM",
        "lugar_evento": "Auditorio Central",
        "referencia_evento": "",
        "nombre_proyecto": "test_project"
    })
    assert response.status_code == 401
    print("✓ Unauthenticated generation correctly rejected")

def test_document_generation(session_id):
    """Test document generation with authenticated session"""
    print("\nTesting document generation...")
    response = requests.post(f"{BASE_URL}/api/generate", json={
        "session_id": session_id,
        "fecha_evento": "15 de Diciembre, 2024",
        "hora_evento": "7:00 PM",
        "lugar_evento": "Auditorio Central",
        "referencia_evento": "Salmo 24:7-10",
        "nombre_proyecto": "integration_test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "documents" in data
    assert len(data["documents"]) == 3
    
    # Check each document type
    doc_types = [doc["type"] for doc in data["documents"]]
    assert "a4" in doc_types
    assert "4x1" in doc_types
    assert "gigantografia" in doc_types
    
    print("✓ Document generation successful")
    print(f"  Generated {len(data['documents'])} documents:")
    for doc in data["documents"]:
        status_icon = "✓" if doc["status"] == "success" else "✗"
        print(f"    {status_icon} {doc['type']}: {doc['filename']}")
    
    return data["documents"]

def test_file_download(documents):
    """Test downloading generated files"""
    print("\nTesting file downloads...")
    for doc in documents:
        if doc["status"] == "success":
            filename = doc["filename"]
            response = requests.get(f"{BASE_URL}/api/download/{filename}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            print(f"  ✓ Downloaded {filename} ({len(response.content)} bytes)")

def test_nonexistent_file_download():
    """Test that downloading nonexistent file returns 404"""
    print("\nTesting nonexistent file download...")
    response = requests.get(f"{BASE_URL}/api/download/nonexistent_file.pdf")
    assert response.status_code == 404
    print("✓ Nonexistent file correctly returns 404")

def test_incorrect_answer_reset():
    """Test that incorrect answer resets to question 1"""
    print("\nTesting incorrect answer reset...")
    
    # Start new session
    response = requests.post(f"{BASE_URL}/api/auth/start-session")
    session_id = response.json()["session_id"]
    
    # Answer question 1 correctly
    response = requests.post(f"{BASE_URL}/api/auth/validate-answer", json={
        "session_id": session_id,
        "question_number": 1,
        "answer": "iglesia central"
    })
    assert response.json()["next_question"] == 2
    
    # Answer question 2 incorrectly
    response = requests.post(f"{BASE_URL}/api/auth/validate-answer", json={
        "session_id": session_id,
        "question_number": 2,
        "answer": "wrong answer"
    })
    data = response.json()
    assert data["success"] == False
    assert data["next_question"] == 1  # Should reset to question 1
    print("✓ Incorrect answer correctly resets to question 1")

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("INTEGRATION TEST: Generador de Recursos Evangelísticos")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health_endpoint()
        
        # Test 2: Authentication flow
        session_id = test_authentication_flow()
        
        # Test 3: Unauthenticated generation
        test_unauthenticated_generation()
        
        # Test 4: Document generation
        documents = test_document_generation(session_id)
        
        # Test 5: File downloads
        test_file_download(documents)
        
        # Test 6: Nonexistent file download
        test_nonexistent_file_download()
        
        # Test 7: Incorrect answer reset
        test_incorrect_answer_reset()
        
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED! ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to the backend server.")
        print("  Make sure the backend is running on http://localhost:8000")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
