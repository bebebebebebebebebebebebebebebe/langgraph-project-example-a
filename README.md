# LangGraph Project Example A

LangChainとLangGraphを使用したマルチエージェントシステムのサンプルプロジェクト。Google Cloud VertexAIとArXiv論文検索機能を統合したAIエージェントを実装しています。

## 概要

このプロジェクトには以下の主要コンポーネントが含まれています：

- **Simple Chatbot**: Gemini 2.0 Flashモデルを使用したシンプルなチャットボット
- **Article Search Agent**: ArXivで論文検索を行うインテリジェントエージェント
- **FastAPI HTTP Server**: RESTful APIエンドポイントを提供するWebサーバー
- **MCP Server**: JSONPlaceholder API統合のためのModel Context Protocolサーバー
- **WordPress Environment**: Docker Composeを使用したWordPress開発環境

## 主要な機能

### 🤖 AI Agents
- **Simple Chatbot** (`src/graphs/simple_chatbot/`): Google Vertex AIのGemini 2.0 Flashモデルを使用したチャットボット
- **Article Search** (`src/graphs/article_search/`): ユーザークエリからArXivで論文検索を行うインテリジェントエージェント

### 🌐 Web Services
- **FastAPI Server** (`src/app/`): シンプルなHTTP APIサーバー
- **MCP Server** (`src/mcp_servers/jsonplaceholder/`): 外部API統合のためのMCPサーバー

### 🔧 Development Tools
- **Docker環境**: WordPress + MySQL + phpMyAdminの開発環境
- **Test Suite**: pytest + pytest-asyncioを使用した非同期テスト環境
- **Code Quality**: ruffによるlintingと自動フォーマット

## 技術スタック

- **フレームワーク**: LangChain, LangGraph, FastAPI
- **AI Models**: Google Vertex AI (Gemini 2.0 Flash)
- **データベース**: MySQL (Docker)
- **言語**: Python 3.13+
- **Package Manager**: uv
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff
- **Container**: Docker, Docker Compose

## セットアップ

### 前提条件

- Python 3.13+
- uv (Pythonパッケージマネージャー)
- Docker & Docker Compose
- Google Cloud サービスアカウントキー (`gcp_cred.json`)

### インストール

1. **依存関係のインストール**:
   ```bash
   uv sync
   ```

2. **開発用依存関係の追加インストール**:
   ```bash
   uv sync --group dev
   ```

3. **環境変数の設定**:
   `.env` ファイルを作成し、以下の変数を設定:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./gcp_cred.json
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   OPENAI_API_KEY=your-openai-api-key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langchain-api-key
   LANGCHAIN_PROJECT=your-project-name
   ```

4. **Google Cloud認証**:
   `gcp_cred.json` ファイルをプロジェクトルートに配置

## 使用方法

### AI Agents

#### Simple Chatbot
```bash
uv run simple-chatbot
```

#### Article Search Agent
```bash
uv run article-search
```

### Web Services

#### FastAPI Server
```bash
uv run graph-server
```
サーバーは `http://localhost:8000` で起動します。

#### MCP Server
```bash
uv run mcp-server-jsonplaceholder
```

### WordPress開発環境

```bash
# WordPress + MySQL + phpMyAdminの起動
docker-compose up -d

# アクセス
# WordPress: http://localhost:8000
# phpMyAdmin: http://localhost:8888
```

## 開発

### テスト実行

```bash
# 全テスト実行
uv run pytest

# カバレッジ付きテスト
uv run pytest --cov

# 特定のテストファイル
uv run pytest tests/mcp_servers/jsonplaceholder/test_jsonplaceholder_mcp.py
```

### コード品質

```bash
# Linting
ruff check .

# 自動修正
ruff check --fix .

# フォーマット
ruff format .
```

### 新しい依存関係の追加

```bash
# 通常の依存関係
uv add package_name

# 開発用依存関係
uv add --group dev package_name
```

## プロジェクト構造

```
├── src/
│   ├── app/                    # FastAPIアプリケーション
│   ├── graphs/                 # LangGraphエージェント定義
│   │   ├── simple_chatbot/     # シンプルチャットボット
│   │   └── article_search/     # 論文検索エージェント
│   ├── mcp_servers/            # MCPサーバー実装
│   │   └── jsonplaceholder/    # JSONPlaceholder API統合
│   ├── config/                 # 設定管理
│   └── utils/                  # ユーティリティ
├── tests/                      # テストファイル
├── langgraph.json              # LangGraphサービス設定
├── pyproject.toml              # プロジェクト設定
├── docker-compose.yaml         # Docker環境定義
└── CLAUDE.md                   # 開発ガイドライン
```

## LangGraph設定

プロジェクトは `langgraph.json` で設定されており、以下のサービスを定義しています：

- **Graphs**: `example-agent` (Simple Chatbot)
- **HTTP App**: FastAPIサーバー
- **Dependencies**: 現在のプロジェクト

## ライセンス

このプロジェクトは学習・研究目的のサンプルプロジェクトです。

## 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 問題報告

バグや機能リクエストは [Issues](../../issues) ページで報告してください。
