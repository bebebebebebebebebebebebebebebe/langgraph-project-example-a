from datetime import datetime, timedelta
from typing import Optional

import arxiv
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

from tools.search_papers.arxiv_searcher import ArxivSearcher
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
    end_time: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(),
        description='End time for filtering results. Defaults to now.',
        example='2023-10-01T00:00:00Z',
    )
    start_time: Optional[datetime] = Field(
        default=None, description='Start time for filtering results. Defaults to None.', example='2023-01-01T00:00:00Z'
    )


class SearchPapersTool(BaseTool):
    """Search for academic papers using the arXiv API."""

    name: str = 'SearchPapersTool'
    description: str = 'Search for academic papers using the arXiv API. Returns a list of documents with metadata.'
    args_schema: Optional[ArgsSchema] = SearchPapersToolInput
    return_direct: bool = False
    arxiv_searcher: ArxivSearcher = ArxivSearcher()

    def _run(
        self,
        query: str,
        max_results: int = 3,
        is_latest: bool = True,
        end_time: Optional[datetime] = None,
        start_time: Optional[datetime] = None,
    ) -> list[Document]:
        """
        Synchronously search for academic papers.

        Args:
            query (str): The search query for academic papers.
            max_results (int): Maximum number of results to return.
            is_latest (bool): Whether to filter results to the latest papers.
            end_time (Optional[datetime]): End time for filtering results.
            start_time (Optional[datetime]): Start time for filtering results.

        Returns:
            list[Document]: List of documents with metadata.
        """
        try:
            start_time, end_time = self._specify_range_of_dates(is_latest, end_time, start_time)
            search_results = self.arxiv_searcher.fetch_arxiv_papers(
                query=query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
            )

            if not search_results:
                raise ValueError(f'No papers found for query: {query}')

            paper_ids = [result.entry_id.split('/')[-1] for result in search_results]
            documents = self.arxiv_searcher.load_arxiv_documents_by_id(paper_ids)
            if not documents:
                raise ValueError(f'No documents found for paper IDs: {paper_ids}')
            return documents

        except Exception as e:
            logger.error(f'Error in SearchPapersTool: {e}')
            raise CallToolError(f'Error in SearchPapersTool: {e}') from e

    async def _arun(
        self,
        query: str,
        max_results: int = 3,
        is_latest: bool = True,
        end_time: Optional[datetime] = None,
        start_time: Optional[datetime] = None,
    ):
        try:
            start_time, end_time = self._specify_range_of_dates(is_latest, end_time, start_time)
            search_results = self.arxiv_searcher.fetch_arxiv_papers(
                query=query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
            )

            if not search_results:
                raise ValueError(f'No papers found for query: {query}')

            paper_ids = [result.entry_id.split('/')[-1] for result in search_results]
            documents = await self.arxiv_searcher.aload_arxiv_documents_by_id(paper_ids)
            if not documents:
                raise ValueError(f'No documents found for paper IDs: {paper_ids}')
            return documents

        except Exception as e:
            logger.error(f'Error in SearchPapersTool: {e}')
            raise CallToolError(f'Error in SearchPapersTool: {e}') from e

    def _specify_range_of_dates(
        self,
        is_latest: bool,
        end_time: Optional[datetime] = None,
        start_time: Optional[datetime] = None,
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        Specify the range of dates for filtering results.

        Args:
            is_latest (bool): Whether to filter results to the latest papers.
            end_time (Optional[datetime]): End time for filtering results.
            start_time (Optional[datetime]): Start time for filtering results.

        Returns:
            tuple[Optional[datetime], Optional[datetime]]: Start and end times for filtering results.
        """
        if not start_time and not end_time:
            end_time = datetime.now()

            if is_latest:
                start_time = end_time - timedelta(days=180)

            else:
                start_time = end_time - timedelta(days=365)

        return (start_time, end_time)
