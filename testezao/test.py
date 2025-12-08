# test_api.py
import requests

BASE_URL = "http://localhost:5000"

print("Testando API PDI...")

# Teste 1: Rota principal
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Rota principal: {response.status_code} - {response.json()}")
except:
    print("❌ Rota principal falhou")

# Teste 2: Criar usuário
try:
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"✅ Registro: {response.status_code}")
except:
    print("❌ Registro falhou")

print("\n🎉 Testes completos! Acesse: http://localhost:5000")