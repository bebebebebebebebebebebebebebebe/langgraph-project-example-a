from typing import Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import MCPConfig

config = MCPConfig()

mcp = FastMCP(
    name=config.NAME,
    version=config.VERSION,
)


class UserParams(BaseModel):
    """
    Parameters for the get_all_users tool.
    """

    id: int | None = Field(None, description='ID of the user to retrieve. If None, retrieves all users.')
    name: str | None = Field(None, description='Name of the user to filter by. If None, retrieves all users.')
    user_name: str | None = Field(
        None,
        description='Username of the user to filter by. If None, retrieves all users.',
    )
    email: str | None = Field(
        None,
        description='Email of the user to filter by. If None, retrieves all users.',
    )


class MCPServerOptions(BaseModel):
    """
    Options for the MCP server.
    """

    transport: str = Field(
        ...,
        description='Transport protocol for the MCP. Options: "sse", "http", "stdio".',
    )
    host: str = Field(..., description='Host address for the MCP server.')
    port: int = Field(..., description='Port number for the MCP server.')


@mcp.tool
async def get_all_users(params: Optional[UserParams | None] = None) -> list:
    """
    Get all users from the JSONPlaceholder API.

    Args:
        params (UserParams): Parameters for the request, including limit.

    Returns:
        list: A list of users.
    """
    try:
        async with httpx.AsyncClient() as client:
            if params:
                response = await client.get(f'{config.BASE_URL}/users', params=params.model_dump())
            else:
                response = await client.get(f'{config.BASE_URL}/users')

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        print(f'HTTP error occurred: {e.response.status_code} - {e.response.text}')
        return []

    except httpx.RequestError as e:
        print(f'Request error occurred: {e}')
        return []

    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return []
