def test_register_creates_user(client):
    response = client.post("/auth/register", json={"email": "new@example.com", "password": "password123"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_is_rejected(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    response = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_rejects_short_password(client):
    response = client.post("/auth/register", json={"email": "short@example.com", "password": "1234"})
    assert response.status_code == 422


def test_login_with_correct_credentials_returns_token(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_is_rejected(client):
    client.post("/auth/register", json={"email": "login2@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "login2@example.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_protected_endpoint_requires_token(client):
    response = client.get("/budgets")
    assert response.status_code == 401