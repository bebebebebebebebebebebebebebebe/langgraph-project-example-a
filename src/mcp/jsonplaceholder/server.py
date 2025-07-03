import asyncio

import click
import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from src.mcp.jsonplaceholder.config import MCPConfig

config = MCPConfig()

mcp = FastMCP(
    name=config.NAME,
    version=config.VERSION,
)


class UserParams(BaseModel):
    """
    Parameters for the get_all_users tool.
    """

    limit: int = Field(default=None, description="Number of users to return")


class MCPServerOptions(BaseModel):
    """
    Options for the MCP server.
    """

    transport: str = Field(
        ...,
        description='Transport protocol for the MCP. Options: "sse", "http", "stdio".',
    )
    host: str = Field(..., description="Host address for the MCP server.")
    port: int = Field(..., description="Port number for the MCP server.")


@mcp.tool
async def get_all_users(params: UserParams) -> list:
    """
    Get all users from the JSONPlaceholder API.

    Args:
        params (UserParams): Parameters for the request, including limit.

    Returns:
        list: A list of users.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{mcp.base_url}/users", params=params.model_dump()
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        mcp.logger.error(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
        return []

    except httpx.RequestError as e:
        mcp.logger.error(f"Request error occurred: {e}")
        return []

    except Exception as e:
        mcp.logger.error(f"An unexpected error occurred: {e}")
        return []


async def init_server(options: MCPServerOptions):
    """
    Initialize and run the MCP server with the given options.

    Args:
        options (MCPServerOptions): Options for the MCP server.
    """
    await mcp.run_async(
        transport=options.transport,
        host=options.host,
        port=options.port,
        path=config.PATH,
    )


@click.command()
@click.option(
    "--transport",
    default=config.TRANSPORT,
    help='Transport protocol for the MCP. Options: "sse", "http", "stdio".',
)
@click.option("--host", default=config.HOST, help="Host address for the MCP server.")
@click.option("--port", default=config.PORT, help="Port number for the MCP server.")
def main(transport: str, host: str, port: int):
    """
    Main entry point for the MCP server.

    Args:
        transport (str): Transport protocol for the MCP.
        host (str): Host address for the MCP server.
        port (int): Port number for the MCP server.
    """
    options = MCPServerOptions(transport=transport, host=host, port=port)
    asyncio.run(init_server(options))


if __name__ == "__main__":
    main()
