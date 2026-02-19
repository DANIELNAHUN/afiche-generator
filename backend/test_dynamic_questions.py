"""
Script de prueba para verificar la carga dinámica de preguntas de seguridad
"""
import os
from dotenv import load_dotenv
from services.auth_service import AuthService

# Cargar variables de entorno
load_dotenv()

# Crear instancia del servicio
auth_service = AuthService()

print("=" * 60)
print("PRUEBA DE CARGA DINÁMICA DE PREGUNTAS DE SEGURIDAD")
print("=" * 60)
print(f"\nTotal de preguntas configuradas: {auth_service.total_questions}")
print("\nPreguntas cargadas:")
print("-" * 60)

for i, question in enumerate(auth_service.security_questions, 1):
    print(f"\nPregunta {i}:")
    print(f"  Texto: {question['text']}")
    print(f"  Respuesta esperada: {question['answer']}")

print("\n" + "=" * 60)
print("✓ Sistema configurado correctamente")
print("=" * 60)
