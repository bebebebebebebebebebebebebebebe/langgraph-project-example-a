# CLAUDE.md

## Conversation Guidelines

- 常に日本語で会話する

## Development Philosophy

### Test-Driven Development (TDD)

- 原則としてテスト駆動開発（TDD）で進める
- 期待される入出力に基づき、まずテストを作成する
- 実装コードは書かず、テストのみを用意する
- テストを実行し、失敗を確認する
- テストが正しいことを確認できた段階でコミットする
- その後、テストをパスさせる実装を進める
- 実装中はテストを変更せず、コードを修正し続ける
- すべてのテストが通過するまで繰り返す

## Development Commands

### Package Management
- **Install dependencies**: `uv sync` or `uv sync --group dev` (for development dependencies)
- **Add new dependency**: `uv add <package_name>`
- **Remove dependency**: `uv remove <package_name>`

### Testing
- **Run all tests**: `uv run pytest`
- **Run tests with coverage**: `uv run pytest --cov`
- **Run specific test file**: `uv run pytest tests/test_server.py`
- **Run single test**: `uv run pytest tests/test_server.py::test_root`

### Code Quality
- **Lint and format**: `ruff check .` and `ruff format .`
- **Fix linting issues**: `ruff check --fix .`

### Running Services
- **Start FastAPI server**: `uv run graph-server` (runs on localhost:8000)
- **Run example agent**: `uv run example-agent`
- **Start MCP server**: `uv run mcp-server-jsonplaceholder`

### LangGraph Development
- **LangGraph Studio**: Use `langgraph.json` configuration for graph development
- **View graph structure**: The example graph is defined in `src/graphs/example_agent/example_graph.py:graph`

### Docker Services
- **Start WordPress stack**: `docker-compose up -d`
- **Stop services**: `docker-compose down`
- **Access WordPress**: http://localhost:8000
- **Access phpMyAdmin**: http://localhost:8888

## Architecture Overview

This is a LangGraph project with multiple components:

### Core Components
1. **LangGraph Agent** (`src/graphs/example_agent/`): Simple chatbot implementation using LangGraph StateGraph
2. **FastAPI HTTP Server** (`src/app/`): Basic web server with health check endpoint
3. **MCP Server** (`src/mcp/jsonplaceholder/`): Model Context Protocol server for JSONPlaceholder API integration

### Key Files
- `langgraph.json`: LangGraph configuration defining graphs and HTTP app
- `pyproject.toml`: Project configuration with scripts, dependencies, and tool settings
- `src/graphs/example_agent/example_graph.py`: Main graph definition with State and chatbot node
- `src/mcp/jsonplaceholder/server.py`: MCP server with get_all_users tool
- `src/mcp/jsonplaceholder/config.py`: Configuration settings for MCP server

### Architecture Patterns
- **State Management**: Uses TypedDict with Annotated messages for LangGraph state
- **Async Operations**: MCP server uses httpx for async HTTP requests
- **Configuration**: Pydantic settings for environment-based configuration
- **Error Handling**: Comprehensive error handling in MCP server with logging
- **Testing**: Pytest with async support and ASGI test client

### Development Workflow
1. LangGraph graphs are defined in `src/graphs/` and referenced in `langgraph.json`
2. The FastAPI app serves as HTTP interface and is configured in `langgraph.json`
3. MCP servers provide external API integration capabilities
4. Tests use pytest with async fixtures for testing FastAPI endpoints

The project follows modern Python practices with uv for dependency management, ruff for linting/formatting, and proper separation of concerns between graph logic, HTTP serving, and external integrations.
