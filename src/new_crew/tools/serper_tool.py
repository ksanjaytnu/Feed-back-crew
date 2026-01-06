from typing import List, Any
import os
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar


class SerperSearchInput(BaseModel):
    query: str = Field(..., description="Search query to run via Serper")
    num_results: int = Field(3, description="Number of top results to return")


class SerperSearchTool(BaseTool):
    name: str = "Serper Search"
    description: str = "Search the web using the Serper API and return the top result snippets and links."
    args_schema: type[BaseModel] = SerperSearchInput

    env_vars: List[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name="SERPER_API_KEY",
                description="Serper API key (set this in env before running).",
                required=True,
            )
        ]
    )

    def _extract_query(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str | None, int]:
        query = kwargs.get("query")
        num_results = int(kwargs.get("num_results", 3))

        if not query and args:
            first = args[0]
            # Accept simple positional strings: _run('query', num_results)
            if isinstance(first, str):
                query = first
                if len(args) > 1:
                    try:
                        num_results = int(args[1])
                    except Exception:
                        pass
            elif isinstance(first, dict):
                query = first.get("query") or first.get("q")
                num_results = int(first.get("num_results", num_results))
                if not query and "properties" in first:
                    props = first["properties"]
                    qprop = props.get("query") or props.get("q")
                    if isinstance(qprop, dict):
                        query = qprop.get("default") or qprop.get("example") or qprop.get("value")
                    else:
                        query = qprop

        return query, num_results

    def _run(self, *args, **kwargs) -> str:
        query, num_results = self._extract_query(args, kwargs)

        if not query:
            return "Serper Search: missing 'query' parameter."

        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            for ev in self.env_vars:
                if ev.name == "SERPER_API_KEY" and getattr(ev, 'default', None):
                    api_key = ev.default

        if not api_key:
            return "SERPER_API_KEY is not set. Please set the environment variable to use SerperSearchTool."

        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        endpoint = "https://google.serper.dev/search"
        payload = {"q": query}

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as he:
            code = getattr(he.response, "status_code", "unknown")
            return f"Serper API request failed: {he} (status={code})"
        except Exception as e:
            return f"Serper API request failed: {e}"

        snippets: List[str] = []
        organic = data.get("organic") or data.get("results") or []

        for item in organic[: max(1, num_results)]:
            title = item.get("title") or item.get("title_raw") or ""
            snippet = item.get("snippet") or item.get("description") or ""
            link = item.get("link") or item.get("url") or ""
            snippets.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")

        if not snippets:
            return f"No results from Serper for query: {query}. Raw response: {data}"

        return "\n\n".join(snippets)
