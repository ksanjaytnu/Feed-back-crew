from typing import List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar


class LocalSummarizerInput(BaseModel):
    raw_text: str = Field(..., description="Raw concatenated search snippets")
    max_items: int = Field(5, description="Max number of bullet points to return")


class LocalSummarizer(BaseTool):
    name: str = "Local Summarizer"
    description: str = "Create a concise summary and list of themes from raw search snippets without calling an LLM."
    args_schema: type[BaseModel] = LocalSummarizerInput

    def _run(self, raw_text: str, max_items: int = 5) -> str:
        if not raw_text or not raw_text.strip():
            return "No text provided to summarize."

        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        # Heuristic: collect titles and snippets
        titles: List[str] = []
        snippets: List[str] = []
        for line in lines:
            if line.lower().startswith("title:"):
                titles.append(line[6:].strip())
            elif line.lower().startswith("snippet:"):
                snippets.append(line[8:].strip())
            elif line.lower().startswith("link:"):
                # ignore links for now
                continue
            else:
                # fallback: treat as snippet
                snippets.append(line)

        # Simple theme extraction via keyword counts
        keywords = [
            "shipping",
            "refund",
            "return",
            "quality",
            "support",
            "price",
            "performance",
            "sustainability",
            "design",
        ]
        counts = {k: 0 for k in keywords}
        for s in snippets + titles:
            sl = s.lower()
            for k in keywords:
                if k in sl:
                    counts[k] += 1

        # Build sorted theme list
        themes = sorted([(k, v) for k, v in counts.items() if v > 0], key=lambda x: -x[1])

        bullets: List[str] = []
        # Add top themes
        for k, v in themes[:max_items]:
            bullets.append(f"{k.capitalize()}: mentioned {v} times in snippets")

        # If no themes, add top snippet highlights
        if not bullets:
            sample_snips = snippets[:max_items]
            for s in sample_snips:
                bullets.append(f"- {s}")

        summary = "\n".join(bullets)
        return f"Summary:\n{summary}\n\nExtracted Titles:\n" + "; ".join(titles[:max_items])
