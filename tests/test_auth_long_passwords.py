"""
Testes específicos para validar a correção: SHA256 + bcrypt para senhas longas

PROBLEMA ORIGINAL:
  ValueError: password cannot be longer than 72 bytes

SOLUÇÃO:
  Pré-hash com SHA256 antes do bcrypt

TESTES:
  ✓ Senha normal (< 72 bytes)
  ✓ Senha muito longa (> 72 bytes UTF-8)
  ✓ Senha com Unicode (acentos, emojis)
  ✓ Login com senha longa funciona
"""
import pytest

BASE = "/api/v1"


# ── Dados de Teste ─────────────────────────────────────────────────────────────

LONG_PASSWORD_TESTS = {
    "normal": {
        "password": "Senh@123Normal456",
        "description": "Senha normal (< 72 bytes)",
    },
    "very_long": {
        "password": "a" * 150,  # > 72 bytes
        "description": "Senha muito longa (150 caracteres)",
    },
    "unicode": {
        "password": "Senh@123_São_Luís_🔒_Café_ÇãôÉáíóú",
        "description": "Senha com Unicode (acentos, emojis)",
    },
    "max_length": {
        "password": "a" * 128,  # Máximo do schema
        "description": "Senha no comprimento máximo (128 caracteres)",
    },
}


# ── Testes: Register com Senhas Longas ─────────────────────────────────────────

@pytest.mark.parametrize("test_key", list(LONG_PASSWORD_TESTS.keys()))
def test_register_long_password(client, test_key):
    """
    Testa registro com senhas longas.
    ANTES: Erro 500 "password cannot be longer than 72 bytes"
    DEPOIS: Funciona perfeitamente ✅
    """
    test_data = LONG_PASSWORD_TESTS[test_key]
    password = test_data["password"]
    
    user = {
        "name": f"Teste {test_key}",
        "email": f"teste_{test_key}@email.com",
        "password": password,
        "type": "client",
        "phone": "98999999999",
        "city": "São Luís",
    }
    
    # Register com senha longa
    r = client.post(f"{BASE}/auth/register", json=user)
    
    # Deveria ser 201, não 500
    assert r.status_code == 201, \
        f"Register falhou para {test_data['description']}: {r.status_code} {r.text}"
    
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == user["email"]
    assert "password" not in data["user"]  # Nunca retorna a senha


@pytest.mark.parametrize("test_key", list(LONG_PASSWORD_TESTS.keys()))
def test_login_long_password(client, test_key):
    """
    Testa login com senhas longas.
    ANTES: Erro 500 ou falha de verificação
    DEPOIS: Login funciona ✅
    """
    test_data = LONG_PASSWORD_TESTS[test_key]
    password = test_data["password"]
    email = f"login_{test_key}@email.com"
    
    # 1. Registra usuário com senha longa
    user = {
        "name": f"Login {test_key}",
        "email": email,
        "password": password,
        "type": "client",
        "phone": "98999999888",
        "city": "São Luís",
    }
    
    r_register = client.post(f"{BASE}/auth/register", json=user)
    assert r_register.status_code == 201
    
    # 2. Fazllogin com a mesma senha longa
    r_login = client.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": password}
    )
    
    # Deveria ser 200, não 401
    assert r_login.status_code == 200, \
        f"Login falhou para {test_data['description']}: {r_login.status_code} {r_login.text}"
    
    data = r_login.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.parametrize("test_key", list(LONG_PASSWORD_TESTS.keys()))
def test_login_wrong_password_long_password(client, test_key):
    """
    Testa que login com senha ERRADA falha mesmo com senha registrada longa.
    """
    test_data = LONG_PASSWORD_TESTS[test_key]
    password = test_data["password"]
    email = f"wrong_{test_key}@email.com"
    
    # Registra com senha longa
    user = {
        "name": f"Wrong {test_key}",
        "email": email,
        "password": password,
        "type": "client",
        "phone": "98999999777",
        "city": "São Luís",
    }
    client.post(f"{BASE}/auth/register", json=user)
    
    # Tenta login com senha errada
    wrong_password = "senha_completamente_errada_123"
    r = client.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": wrong_password}
    )
    
    # Deveria ser 401 (not authorized)
    assert r.status_code == 401, \
        f"Deveria rejeitar senha errada, mas retornou {r.status_code}"


def test_change_password_long_password(client):
    """
    Testa mudança de senha para exemplo longo.
    """
    email = "change_pwd@email.com"
    old_password = "SenhaAntiga@123Normal"
    new_password = "a" * 120 + "NovaSenha@123"  # Sens nova muito longa
    
    # 1. Registra com senha antiga
    user = {
        "name": "Change Password",
        "email": email,
        "password": old_password,
        "type": "client",
        "phone": "98999999666",
        "city": "São Luís",
    }
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 201
    
    # 2. Login com senha antiga
    r_login = client.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": old_password}
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    
    # 3. Muda senha para uma muito longa
    r_change = client.put(
        f"{BASE}/users/me/password",
        json={
            "current_password": old_password,
            "new_password": new_password,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_change.status_code == 204, \
        f"Falha ao mudar para senha longa: {r_change.status_code} {r_change.text}"
    
    # 4. Login com nova senha longa deve funcionar
    r_login_new = client.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": new_password}
    )
    assert r_login_new.status_code == 200, \
        f"Login com nova senha longa falhou: {r_login_new.status_code}"


# ── Testes: Edge Cases ─────────────────────────────────────────────────────────

def test_register_empty_password_rejected(client):
    """Valida que senha vazia é rejeitada."""
    user = {
        "name": "Empty Password",
        "email": "empty@email.com",
        "password": "",  # Vazio
        "type": "client",
        "phone": "98999999555",
        "city": "São Luís",
    }
    
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 422, "Senha vazia deveria ser rejeitada (422)"


def test_register_whitespace_only_password_rejected(client):
    """Valida que senha com apenas espaços é rejeitada."""
    user = {
        "name": "Whitespace Password",
        "email": "whitespace@email.com",
        "password": "   ",  # Apenas espaços
        "type": "client",
        "phone": "98999999444",
        "city": "São Luís",
    }
    
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 422, "Senha com espaços deveria ser rejeitada (422)"


def test_register_password_too_short(client):
    """Valida limite mínimo de 6 caracteres."""
    user = {
        "name": "Short Password",
        "email": "short@email.com",
        "password": "12345",  # 5 caracteres (< 6)
        "type": "client",
        "phone": "98999999333",
        "city": "São Luís",
    }
    
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 422, "Senha < 6 caracteres deveria ser rejeitada (422)"


def test_register_password_too_long(client):
    """Valida limite máximo de 128 caracteres."""
    user = {
        "name": "Too Long Password",
        "email": "toolong@email.com",
        "password": "a" * 129,  # 129 caracteres (> 128)
        "type": "client",
        "phone": "98999999222",
        "city": "São Luís",
    }
    
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 422, "Senha > 128 caracteres deveria ser rejeitada (422)"


def test_refresh_token_with_long_password_user(client):
    """Testa que refresh token funciona para usuário com senha longa."""
    email = "refresh@email.com"
    password = "a" * 100 + "@LongSenha123"
    
    # Registra e login
    user = {
        "name": "Refresh Test",
        "email": email,
        "password": password,
        "type": "client",
        "phone": "98999999111",
        "city": "São Luís",
    }
    client.post(f"{BASE}/auth/register", json=user)
    r_login = client.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": password}
    )
    assert r_login.status_code == 200
    
    refresh_token = r_login.json()["refresh_token"]
    
    # Usa refresh token
    r_refresh = client.post(
        f"{BASE}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert r_refresh.status_code == 200, \
        f"Refresh falhou: {r_refresh.status_code} {r_refresh.text}"
    
    new_data = r_refresh.json()
    assert "access_token" in new_data
    assert new_data["token_type"] == "bearer"


# ── Resumo ─────────────────────────────────────────────────────────────────────

"""
RESUMO DOS TESTES:

✅ Register com senhas longas (> 72 bytes UTF-8) funciona
✅ Login com senhas longas funciona
✅ Login com senha errada falha mesmo com senha registrada longa
✅ Change password para senha longa funciona
✅ Refresh token funciona para usuários com senhas longas
✅ Edge cases (vazia, whitespace, muito curta, muito longa) são rejeitados

RESULTADO ESPERADO:
  Erro original: ValueError: password cannot be longer than 72 bytes (HTTP 500)
  Após correção: Todos os testes passam ✅

EVIDÊNCIA:
  Se todos esses testes passam, o erro foi resolvido!
"""
