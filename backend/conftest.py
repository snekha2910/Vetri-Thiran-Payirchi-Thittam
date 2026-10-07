import os
import pytest
from fastapi.testclient import TestClient

# Configure test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://mock-test.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock-service-key"
os.environ["GEMINI_API_KEY"] = "mock-gemini-key"
os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"

from app.main import app
from app.core.security import create_access_token

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers():
    token = create_access_token("user_12345", email="primary.user@example.com")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user_headers():
    token = create_access_token("user_67890", email="secondary.user@example.com")
    return {"Authorization": f"Bearer {token}"}
