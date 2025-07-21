import asyncio
from datetime import datetime, timedelta
from typing import Optional

import arxiv
from langchain_community.document_loaders import ArxivLoader
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

from utils.logger import get_logger

logger = get_logger(__name__)


class CallToolError(Exception):
    """Custom exception for call tool errors."""

    pass


class SearchPapersToolInput(BaseModel):
    """Input schema for the SearchPapersTool."""

    query: str = Field(..., description='The search query for academic papers.', example='machine learning')
    max_results: int = Field(default=3, description='Maximum number of results to return.', example=5)
    is_latest: bool = Field(default=True, description='Whether to filter results to the latest papers.', example=True)


class SearchPapersTool(BaseTool):
    """Search for academic papers using the arXiv API."""

    name: str = 'SearchPapersTool'
    description: str = 'Search for academic papers using the arXiv API. Returns a list of documents with metadata.'
    args_schema: Optional[ArgsSchema] = SearchPapersToolInput
    return_direct: bool = False
    client: arxiv.Client = arxiv.Client()

    def _run(
        self,
        query: str,
        max_results: int = 3,
        is_latest: bool = True,
    ) -> list[Document]:
        raise NotImplementedError('This tool does not support synchronous execution. Use the async version instead.')

    async def _arun(
        self,
        query: str,
        max_results: int = 3,
        is_latest: bool = True,
    ):
        try:
            search_results = self._search_arxiv_papers(
                query=query,
                is_latest=is_latest,
                max_results=max_results,
            )
            docs = await self._convert_to_documents(search_results)
            if not docs:
                raise CallToolError('No documents found for the given query.')

            return docs
        except Exception as e:
            raise CallToolError(f'Error searching papers: {e}') from e

    async def _convert_to_documents(self, search_results: list[arxiv.Result]) -> list[Document]:
        """
        Convert arXiv search results to a list of Document objects.

        Args:
            search_results (list[arxiv.Result]): List of search results from arXiv.

        Returns:
            list[Document]: List of Document objects containing the paper metadata and content.

        Raises:
            Exception: If an error occurs during the conversion process.
        """
        future_tasks = []
        load_tasks = []

        try:
            for result in search_results:
                loader_query = result.pdf_url.split('/')[-1]
                pdf_loader = ArxivLoader(query=loader_query)
                future_tasks.append(pdf_loader.aload())

            load_docs = await asyncio.gather(*future_tasks)

            for docs in load_docs:
                if not docs:
                    logger.warning(f'No documents found for query: {loader_query}')
                    continue

                load_tasks.append(docs[0])

            return load_tasks

        except Exception as e:
            logger.error(f'Error converting ArXiv results to documents: {e}')
            return []

    def _search_arxiv_papers(
        self,
        query: str,
        is_latest: bool,
        max_results: int,
    ) -> list[arxiv.Result]:
        """
        Search for academic papers on arXiv using the provided query.

        Args:
            query (str): The search query for academic papers.
            is_latest (bool): Whether to filter results to the latest papers.
            max_results (int): Maximum number of results to return.

        Returns:
            list[arxiv.Result]: List of search results from arXiv.

        Raises:
            ValueError: If the query is empty.
            Exception: If an error occurs during the search.
        """
        if not query:
            raise ValueError('Query cannot be empty')
        try:
            if is_latest:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=180)
                start_date_str = start_time.strftime('%Y%m%d')
                end_date_str = end_time.strftime('%Y%m%d')
                search_query = f'{query} AND submittedDate:[{start_date_str} TO {end_date_str}]'
            else:
                search_query = query

            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )
            return list(self.client.results(search))

        except Exception as e:
            logger.error(f'Error searching Arxiv: {e}')
            return []
