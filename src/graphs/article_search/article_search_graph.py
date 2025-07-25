import os
import re
from datetime import datetime, timedelta
from typing import Optional, TypedDict

import arxiv
from dotenv import load_dotenv
from google.oauth2 import service_account
from langchain_community.document_loaders import ArxivLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)


class ArxivQuery(BaseModel):
    keywords: str = Field(description='ArXivで検索するための英語のキーワード')
    latest: bool = Field(description='ユーザーが最新の論文を求めている場合はtrue、そうでない場合はfalse', default=False)


class ArticleSearchState(BaseModel):
    """
    ArticleSearchStateは、ArXivでの論文検索に関連する状態を表します。

    Attributes:
        user_query (str): ユーザーが入力した検索クエリ。
        search_query (ArxivQuery): ArXivでの論文検索に使用するクエリ。
        results (list[Document]): 検索結果として取得された論文のリスト。
    """

    user_query: str = Field(description='ユーザーが入力した検索クエリ', default='ArXivで最新のAIに関する論文を探しています。')
    search_query: Optional[ArxivQuery] = Field(description='ArXivでの論文検索に使用するクエリ', default=None)
    papers: list[Document] = Field(description='検索結果として取得された論文のリスト', default_factory=list)


class ArticleSearchGraph:
    def __init__(self, llm: Optional[ChatVertexAI] = None):
        """
        ArticleSearchGraphのコンストラクタ
        このクラスは、ArXivでの論文検索を行うためのワークフローを定義します。

        主要な機能は、ユーザーの質問から検索クエリを生成し、そのクエリを使用してArXivで論文を検索することです。

        具体的には、以下の2つのノードを持つワークフローを構築します。
        1. ユーザーの質問から検索クエリを生成するノード
        2. 生成された検索クエリを使用してArXivで論文を検索するノード

        これらのノードは、状態管理を通じて連携し、最終的な検索結果を提供します。

        なお、LLM（大規模言語モデル）としてGoogle CloudのVertex AIを使用します。
        LLMの初期化には、Google Cloudのサービスアカウントキーが必要です。

        Args:
            llm (Optional[ChatVertexAI]): 使用するLLMインスタンス。指定しない場合は、Google Cloudのサービスアカウントキーを使用して初期化されます。
        """
        self._llm = llm or self._init_llm()
        self._workflow_builder = StateGraph(ArticleSearchState)
        self._runnable_workflow = self._build_workflow()

    @property
    def runnable_workflow(self) -> CompiledStateGraph:
        """
        ワークフローを実行可能な形で取得するプロパティ

        Returns:
            CompiledStateGraph: 実行可能なワークフロー
        """
        return self._runnable_workflow

    def _build_workflow(self) -> CompiledStateGraph:
        """
        ワークフローを構築する関数

        この関数は、ArXivでの論文検索を行うためのワークフローを構築します。
        ワークフローは、ユーザーの質問から検索クエリを生成し、そのクエリを使用してArXivで論文を検索する2つのノードで構成されています。

        Returns:
            CompiledStateGraph: 構築されたワークフロー
        """
        self._workflow_builder.add_node('generate_search_query', self._generate_search_query_node)
        self._workflow_builder.add_node('search_arxiv_papers', self._search_arxiv_papers_node)
        self._workflow_builder.add_edge('generate_search_query', 'search_arxiv_papers')
        self._workflow_builder.set_entry_point('generate_search_query')
        self._workflow_builder.set_finish_point('search_arxiv_papers')
        return self._workflow_builder.compile()

    def _init_llm(self) -> ChatVertexAI:
        """
        LLMを初期化する関数
        Google Cloudのサービスアカウントキーを使用して認証します。

        Returns:
            ChatVertexAI: 初期化されたLLMインスタンス
        Raises:
            ValueError: Google CloudのサービスアカウントキーまたはプロジェクトIDが設定されていない場合
        """
        if not config.GOOGLE_APPLICATION_CREDENTIALS or not config.GOOGLE_CLOUD_PROJECT:
            raise ValueError('Google CloudのサービスアカウントキーまたはプロジェクトIDが設定されていません。')

        credentials = service_account.Credentials.from_service_account_file(config.GOOGLE_APPLICATION_CREDENTIALS)
        llm = ChatVertexAI(
            model_name='gemini-2.0-flash',
            credentials=credentials,
            project=config.GOOGLE_CLOUD_PROJECT,
        )
        return llm

    async def _search_arxiv_papers_node(self, state: ArticleSearchState) -> ArticleSearchState:
        """
        ArXivで論文を検索するノード

        Args:
            state (ArticleSearchState): 検索クエリと結果を含む状態

        Returns:
            ArticleSearchState: 検索結果を含む状態
        """
        query_obj = state.search_query
        search_results = self._search_arxiv_papers(query_obj)

        if not search_results:
            logger.warning('ArXiv検索結果が見つかりませんでした。')
            return {'query': query_obj, 'results': []}

        documents = await self._convert_to_documents(search_results)

        if not documents:
            logger.warning('ArXivの検索結果をDocumentに変換できませんでした。')
            return {'query': query_obj, 'results': []}

        return {
            'papers': documents,
        }

    def _generate_search_query_node(self, state: ArticleSearchState) -> ArticleSearchState:
        parser = PydanticOutputParser(pydantic_object=ArxivQuery)
        system_instruction = (
            'あなたはArXivで論文を検索するためのエキスパートです。\n'
            '以下のユーザーの質問から、ArXiv論文検索に適した英語のキーワードと、最新の論文を求めているかどうかを抽出し、指定されたJSON形式で回答してください。\n\n'
            'JSON形式: {format_instructions}'
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ('system', system_instruction),
                ('user', 'ユーザーの質問: {user_query}'),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        generate_query_chain = prompt_template | self._llm | parser
        search_query: ArxivQuery = generate_query_chain.invoke({'user_query': state.user_query})

        return {
            'search_query': search_query,
        }

    async def _convert_to_documents(self, search_results: list[arxiv.Result]) -> list[Document]:
        """
        ArXivの検索結果をDocumentオブジェクトのリストに変換する関数

        Args:
            search_results (list[arxiv.Result]): ArXivの検索結果

        Returns:
            list[Document]: Documentオブジェクトのリスト
        """
        documents = []
        try:
            for result in search_results:
                pdf_query = result.pdf_url.split('/')[-1]
                pdf_loader = ArxivLoader(query=pdf_query)
                pdf_docs = pdf_loader.load()
                if not pdf_docs:
                    logger.warning(f'PDFドキュメントが見つかりませんでした: {result.pdf_url}')
                    continue

                documents.append(pdf_docs[0])

            return documents

        except Exception as e:
            logger.error(f'ArXivの検索結果をDocumentに変換中にエラーが発生しました: {e}')
            return []

    def _search_arxiv_papers(self, query_obj: ArxivQuery, max_docs: int = 5):
        """
        ArXivで論文を検索する関数（Pydanticオブジェクトを受け取る）

        Args:
            query_obj (ArxivQuery): 検索クエリを含むPydanticオブジェクト
            max_docs (int): 取得する最大ドキュメント数

        Returns:
            list[Result]: ArXivの検索結果のリスト
        """
        try:
            query = query_obj.keywords

            if query_obj.latest:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=180)  # 過去180日間の論文を検索
                start_date_str = start_date.strftime('%Y%m%d')
                end_date_str = end_date.strftime('%Y%m%d')
                query += f' AND submittedDate:[{start_date_str} TO {end_date_str}]'

            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_docs,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            results = list(client.results(search))
            return results
        except Exception as e:
            print(f'ArXiv検索エラー: {e}')
            return []
