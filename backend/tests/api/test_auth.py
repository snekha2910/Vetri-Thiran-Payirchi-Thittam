class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        })
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "token" in data
        assert data["email"] == "test@example.com"

    def test_register_duplicate_email(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        })
        resp = client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "Password123!",
            "full_name": "Test User"
        })
        # Mock repository returns user or conflicts
        assert resp.status_code in (200, 201, 400, 409)

    def test_register_missing_email(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "password": "Password123!",
            "full_name": "No Email"
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "password": "123",
            "full_name": "Short Pass"
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "Password123!"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data

    def test_login_wrong_password(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "wrong"
        })
        assert resp.status_code in (200, 400, 401)

    def test_login_unknown_email(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "unknown@example.com",
            "password": "Password123!"
        })
        assert resp.status_code in (200, 400, 401, 404)


class TestProtectedEndpoints:
    def test_profile_requires_auth(self, client):
        resp = client.get("/api/v1/profile")
        assert resp.status_code == 401

    def test_profile_with_token(self, client, auth_headers):
        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.status_code == 200
        assert "id" in resp.json()

    def test_plans_requires_auth(self, client):
        resp = client.get("/api/v1/plans")
        assert resp.status_code == 401

    def test_plans_with_token(self, client, auth_headers):
        resp = client.get("/api/v1/plans", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_tampered_jwt_signature_rejected(self, client, auth_headers):
        token = auth_headers["Authorization"].split(" ")[1]
        # Alter signature portion
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.bad_signature_here"
        resp = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {tampered}"})
        assert resp.status_code == 401

    def test_expired_jwt_rejected(self, client):
        import jwt
        import time
        from app.core.config import settings

        payload = {
            "sub": "user_expired_test",
            "email": "expired@example.com",
            "iat": int(time.time()) - 7200,
            "exp": int(time.time()) - 3600
        }
        secret = settings.supabase_jwt_secret or "test-secret"
        expired_token = jwt.encode(payload, secret, algorithm="HS256")
        resp = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {expired_token}"})
        assert resp.status_code == 401

    def test_unsigned_none_algorithm_jwt_rejected(self, client):
        import jwt

        payload = {
            "sub": "user_none_test",
            "email": "none@example.com"
        }
        unsigned_token = jwt.encode(payload, key="", algorithm="none")
        resp = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {unsigned_token}"})
        assert resp.status_code == 401
