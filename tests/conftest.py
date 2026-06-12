import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Provide sample activity data"""
    return {
        "name": "Chess Club",
        "email": "test@mergington.edu"
    }
