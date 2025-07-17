import click

from .config import MCPConfig
from .server import mcp

config = MCPConfig()


@click.command()
@click.option(
    '--transport',
    default=config.TRANSPORT,
    help='Transport protocol for the MCP. Options: "sse", "http", "stdio".',
)
@click.option('--host', default=config.HOST, help='Host address for the MCP server.')
@click.option('--port', default=config.PORT, help='Port number for the MCP server.')
def main(transport: str, host: str, port: int):
    """
    Main entry point for the MCP server.

    Args:
        transport (str): Transport protocol for the MCP.
        host (str): Host address for the MCP server.
        port (int): Port number for the MCP server.
    """
    mcp.run(
        transport=transport,
        host=host,
        port=port,
        path=config.PATH,
    )


if __name__ == '__main__':
    main()
