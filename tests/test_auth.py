"""
Testes de autenticação — cobre os cenários que causavam erro 500.
"""
import pytest

BASE = "/api/v1"

VALID_USER = {
    "name": "João Silva",
    "email": "joao@teste.com",
    "password": "senha1234",
    "type": "client",
    "phone": "98999999999",
    "city": "São Luís",
}


# ── /auth/register ─────────────────────────────────────────────────────────────

def test_register_success(client):
    r = client.post(f"{BASE}/auth/register", json=VALID_USER)
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == VALID_USER["email"]
    # Senha nunca deve aparecer no response
    assert "password" not in data["user"]
    assert "hashed_password" not in data["user"]


def test_register_duplicate_email(client):
    client.post(f"{BASE}/auth/register", json=VALID_USER)
    r = client.post(f"{BASE}/auth/register", json=VALID_USER)
    assert r.status_code == 409
    assert "e-mail" in r.json()["detail"].lower()


def test_register_invalid_email(client):
    bad = {**VALID_USER, "email": "nao-e-email", "phone": "99999999991"}
    r = client.post(f"{BASE}/auth/register", json=bad)
    assert r.status_code == 422


def test_register_short_password(client):
    bad = {**VALID_USER, "email": "curto@teste.com", "password": "123", "phone": "99999999992"}
    r = client.post(f"{BASE}/auth/register", json=bad)
    assert r.status_code == 422


def test_register_missing_fields(client):
    r = client.post(f"{BASE}/auth/register", json={"email": "incompleto@teste.com"})
    assert r.status_code == 422


def test_register_type_field_compatibility(client):
    """Garante que o campo 'type' do Flutter é aceito e mapeado corretamente."""
    user = {**VALID_USER, "email": "prof@teste.com", "type": "professional", "phone": "99999999993"}
    r = client.post(f"{BASE}/auth/register", json=user)
    assert r.status_code == 201
    # Flutter espera receber "type" no response
    assert r.json()["user"]["type"] == "professional"


# ── /auth/login ────────────────────────────────────────────────────────────────

def test_login_success(client):
    client.post(f"{BASE}/auth/register", json={**VALID_USER, "email": "login@teste.com", "phone": "99999999994"})
    r = client.post(f"{BASE}/auth/login", json={"email": "login@teste.com", "password": "senha1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post(f"{BASE}/auth/register", json={**VALID_USER, "email": "wp@teste.com", "phone": "99999999995"})
    r = client.post(f"{BASE}/auth/login", json={"email": "wp@teste.com", "password": "errada"})
    assert r.status_code == 401


def test_login_nonexistent_email(client):
    r = client.post(f"{BASE}/auth/login", json={"email": "fantasma@teste.com", "password": "senha1234"})
    assert r.status_code == 401


def test_login_invalid_email_format(client):
    r = client.post(f"{BASE}/auth/login", json={"email": "nao-e-email", "password": "senha1234"})
    assert r.status_code == 422


# ── /users/me ─────────────────────────────────────────────────────────────────

def _register_and_login(client, suffix: str) -> str:
    u = {**VALID_USER, "email": f"me{suffix}@teste.com", "phone": f"9{suffix}"}
    client.post(f"{BASE}/auth/register", json=u)
    r = client.post(f"{BASE}/auth/login", json={"email": u["email"], "password": u["password"]})
    return r.json()["access_token"]


def test_get_me_authenticated(client):
    token = _register_and_login(client, "01")
    r = client.get(f"{BASE}/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "me01@teste.com"


def test_get_me_unauthenticated(client):
    r = client.get(f"{BASE}/users/me")
    assert r.status_code == 403


def test_get_me_invalid_token(client):
    r = client.get(f"{BASE}/users/me", headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
