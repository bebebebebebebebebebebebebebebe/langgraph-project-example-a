from openai import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPConfig(BaseSettings):
    """
    Configuration settings for the jsonplaceholder MCP.
    """
    VERSION: str = Field(
        default="0.1.0",
        description="Version of the MCP.",
        examples=["0.1.0", "1.0.0"]
    )
    NAME: str = Field(
        default="jsonplaceholder mcp",
        description="Name of the MCP.",
        examples=["jsonplaceholder mcp", "example MCP"]
    )
    TRANSPORT: str = Field(
        default="sse",
        description="Transport protocol for the MCP. Options: 'sse' (Server-Sent Events), 'http' (HTTP/HTTPS), stdio (standard input/output).",
        examples=["sse", "http", "stdio"],
    )
    HOST: str = Field(
        default="localhost",
        description="Host address for the MCP server.",
        examples=["localhost", "0.0.0.0"]
    )
    PORT: int = Field(
        default=5000,
        description="Port number for the MCP server.",
        examples=[8000, 8080, 5000]
    )
    PATH: str = Field(
        default="/mcp",
        description="Path for the MCP server endpoint.",
        examples=["/mcp"]
    )
