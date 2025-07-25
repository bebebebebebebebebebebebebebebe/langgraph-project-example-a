import json
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastmcp.client import Client
from src.mcp_servers.jsonplaceholder import mcp
from src.mcp_servers.jsonplaceholder.server import UserParams


@pytest_asyncio.fixture
async def test_mcp_client() -> AsyncGenerator[Client, None]:
    async with Client(mcp) as client:
        yield client


@pytest.mark.asyncio
async def test_get_all_users(test_mcp_client: Client):
    result = await test_mcp_client.call_tool(
        'get_all_users',
    )
    assert result is not None
    assert result.content[0].text is not None
    data = json.loads(result.content[0].text)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_user_by_id(test_mcp_client: Client):
    user_id = 1
    result = await test_mcp_client.call_tool(
        'get_user_by_id',
        {'user_id': user_id},
    )
    assert result is not None
    assert result.content[0].text is not None
    data = json.loads(result.content[0].text)
    assert data.get('id') == user_id
