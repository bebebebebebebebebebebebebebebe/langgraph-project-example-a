import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.app import app


@pytest_asyncio.fixture
async def test_client():
    url = 'http://testserver'
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=url) as client:
        yield client


@pytest.mark.asyncio
async def test_root(test_client):
    response = await test_client.get('/hello')
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}
