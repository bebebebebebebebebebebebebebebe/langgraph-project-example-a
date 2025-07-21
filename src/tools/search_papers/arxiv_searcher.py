import asyncio
from datetime import datetime

import arxiv
from langchain_community.document_loaders.arxiv import ArxivLoader
from langchain_core.documents import Document


class ArxivSearcherError(Exception):
    """Custom exception for ArxivSearcher errors."""

    pass


class ArxivSearcher:
    def __init__(self):
        self.client = arxiv.Client()

    def load_arxiv_document_by_id(self, paper_id: str) -> Document:
        """
        arxiv論文をIDで取得し、Document形式で返します。

        Args:
            paper_id (str): arXivの論文ID（例: "2101.00001"）

        Returns:
            Document: 論文の詳細情報を含むDocumentオブジェクト
        """
        arxiv_loader = ArxivLoader(
            query=f'{paper_id}',
            top_k_results=1,
        )
        return arxiv_loader.load()[0]

    def load_arxiv_documents_by_id(self, paper_ids: list[str]) -> list[Document]:
        """
        複数のarxiv論文をIDリストから取得し、Document形式で返します。

        Args:
            paper_ids (list[str]): arXivの論文IDのリスト（例: ["2101.00001", "2101.00002"]）

        Returns:
            list[Document]: 論文の詳細情報を含むDocumentオブジェクトのリスト
        """
        loader = ArxivLoader(
            query=' '.join(paper_ids),
            top_k_results=len(paper_ids),
        )
        documents = loader.load()
        if not documents:
            raise ValueError(f'No papers found for IDs: {paper_ids}')
        return documents

    async def aload_arxiv_documents_by_id(self, paper_ids: list[str]) -> list[Document]:
        """
        非同期で複数のarxiv論文をIDリストから取得し、Document形式で返します。

        Args:
            paper_ids (list[str]): arXivの論文IDのリスト（例: ["2101.00001", "2101.00002"]）

        Returns:
            list[Document]: 論文の詳細情報を含むDocumentオブジェクトのリスト
        """
        loader = ArxivLoader(
            query=' '.join(paper_ids),
            top_k_results=len(paper_ids),
        )
        documents = await loader.aload()
        if not documents:
            raise ValueError(f'No papers found for IDs: {paper_ids}')
        return documents

    def get_paper_by_id(self, paper_id) -> arxiv.Result:
        """
        arxiv論文をIDで取得します。

        Args:
            paper_id (str): arXivの論文ID（例: "2101.00001"）

        Returns:
            arxiv.Result: 論文の詳細情報
        """
        try:
            result = arxiv.Search(
                query=f'id:{paper_id}',
                max_results=1,
            )
            results = list(self.client.results(result))
            if results:
                return results[0]
            else:
                raise ValueError(f'Paper with ID {paper_id} not found.')

        except Exception as e:
            raise ArxivSearcherError(f'Arxiv Searcher Error: {e}') from e

    def fetch_arxiv_papers(
        self,
        query: str,
        max_results: int = 10,
        start_time: datetime = None,
        end_time: datetime = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate,
    ) -> list[arxiv.Result]:
        try:
            if start_time and end_time:
                query += f' AND submittedDate:[{start_time.strftime("%Y-%m-%d")} TO {end_time.strftime("%Y-%m-%d")}]'

            elif start_time:
                query += f' AND submittedDate:[{start_time.strftime("%Y-%m-%d")} TO *]'

            elif end_time:
                query += f' AND submittedDate:[* TO {end_time.strftime("%Y-%m-%d")}]'
            search = arxiv.Search(query, max_results=max_results, sort_by=sort_by)
            results = list(self.client.results(search))

            if not results:
                raise ValueError(f'No papers found for query: {query}')

            return results
        except Exception as e:
            raise ArxivSearcherError(f'Arxiv Searcher Error: {e}') from e
