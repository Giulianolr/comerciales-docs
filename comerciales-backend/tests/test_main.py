"""
Tests para el endpoint raíz de la aplicación.
TDD: Test escrito ANTES del código.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_root_endpoint_returns_ok():
    """
    DADO: Un cliente HTTP
    CUANDO: Hace GET a /
    ENTONCES: Recibe 200 con JSON {"status": "ok"}
    """
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
