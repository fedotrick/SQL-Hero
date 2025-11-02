import httpx
import pytest
from httpx import ASGITransport

from app.main import app


@pytest.fixture
async def client():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_root(client: httpx.AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert data["app"] == "Backend API"
    assert data["version"] == "0.1.0"


async def test_health(client: httpx.AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data
    assert data["app"] == "Backend API"
    assert data["version"] == "0.1.0"
