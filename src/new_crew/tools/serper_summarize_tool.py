from typing import Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from .serper_tool import SerperSearchTool
from .local_summarizer import LocalSummarizer


class SerperSummarizeInput(BaseModel):
    query: str = Field(..., description="Search query to run via Serper")
    num_results: int = Field(3, description="Number of top results to fetch from Serper")
    max_items: int = Field(5, description="Max number of bullet points in the local summary")


class SerperSummarizeTool(BaseTool):
    name: str = "Serper Summarize"
    description: str = (
        "Run a Serper web search and produce a short, local summary to minimize LLM usage."
    )
    args_schema: type[BaseModel] = SerperSummarizeInput

    def _run(self, *args: Any, **kwargs: Any) -> str:
        # Accept same flexible inputs as SerperSearchTool
        query = kwargs.get("query") if "query" in kwargs else (args[0] if args else None)
        num_results = int(kwargs.get("num_results", 3))
        max_items = int(kwargs.get("max_items", 5))

        if isinstance(query, dict):
            query = query.get("query") or query.get("q")

        if not query or not isinstance(query, str):
            return "SerperSummarizeTool: missing 'query' parameter."

        # Run Serper search
        serper = SerperSearchTool()
        raw = serper._run(query, num_results)

        # If Serper returned an error-like string, pass it through
        if raw.startswith("Serper API request failed") or raw.startswith("No results from Serper") or raw.startswith("SERPER_API_KEY"):
            return raw

        # Run local summarizer on raw snippets
        summarizer = LocalSummarizer()
        summary = summarizer._run(raw, max_items)

        # Return a compact payload intended for LLM consumption
        return summary
