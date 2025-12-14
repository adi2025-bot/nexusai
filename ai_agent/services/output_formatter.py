import re
from ai_agent.core.schemas import Source
from typing import List, Tuple

class OutputFormatter:
    @staticmethod
    def extract_sources(text: str) -> Tuple[str, List[Source]]:
        """
        Extracts URLs and attempts to create Source objects from text.
        Cleans up the text body slightly.
        """
        # Regex to find standard URLs
        url_pattern = r'(https?://\S+)'
        urls = re.findall(url_pattern, text)
        unique_urls = list(set(urls))
        
        sources = []
        for url in unique_urls:
            # Basic cleanup of punctuation at end of URL
            url = url.rstrip('.,;)')
            sources.append(Source(title="External Link", url=url, snippet="Referred to in response."))

        cleaned_text = text
        return cleaned_text, sources

    @staticmethod
    def format_as_markdown(text: str, sources: List[Source], reasoning_chain: list) -> str:
        md = text + "\n\n"
        
        # Sources Section
        if sources:
            md += "### 📚 Sources\n"
            for i, source in enumerate(sources, 1):
                md += f"{i}. [{source.title}]({source.url})\n"
        
        # Reasoning Dropdown
        if reasoning_chain:
             md += "\n---\n<details><summary>🧠 View Reasoning Process</summary>\n\n"
             for step in reasoning_chain:
                 md += f"**Step {step.step_number} (Tool: `{step.tool}`)**\n"
                 md += f"- *Thought:* {step.thought}\n"
                 md += f"- *Input:* `{step.tool_input}`\n"
                 md += f"- *Observation:* {step.observation}\n\n"
             md += "</details>"
        return md
