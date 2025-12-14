import json
from typing import Dict, Callable
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS

# --- Tool Definitions ---

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The specific query to search for on the internet.")

class CalculatorSchema(BaseModel):
    expression: str = Field(..., description="A mathematical expression to evaluate (e.g., '23 * 45 / 1.5').")

# --- Tool Implementations ---

class ToolRegistry:
    def __init__(self):
        self.ddgs = DDGS()
        self.tools: Dict[str, Callable] = {
            "web_search": self.web_search,
            "calculator": self.calculator,
        }
    
    def get_tool_names(self) -> str:
        return ", ".join(self.tools.keys())

    async def web_search(self, query: str) -> str:
        """Executes a search using DuckDuckGo."""
        try:
            results = self.ddgs.text(query, max_results=5)
            if not results:
                return "No relevant search results found."
            
            # Format results
            formatted_results = [f"Source: {r['href']}\nTitle: {r['title']}\nSnippet: {r['body']}" for r in results]
            return "\n\n---\n\n".join(formatted_results)
        except Exception as e:
            return f"Search failed: {str(e)}"

    async def calculator(self, expression: str) -> str:
        """Safe evaluation of math expressions."""
        allowed_chars = "0123456789+-*/()., "
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in mathematical expression."
        try:
            # pylint: disable=eval-used
            result = eval(expression, {"__builtins__": None}, {})
            return str(result)
        except Exception as e:
            return f"Calculation failed: {str(e)}"

    async def execute(self, tool_name: str, tool_input: str) -> str:
        """Universal execution handler."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        try:
            return await self.tools[tool_name](tool_input)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
