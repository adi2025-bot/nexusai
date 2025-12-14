from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum

# --- Enums ---
class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    REPORT = "report"

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    CRITIC = "critic"

# --- Shared Models ---
class Source(BaseModel):
    title: str
    url: str
    snippet: str
    credibility_score: Optional[float] = Field(default=None, ge=0, le=1)

class ReasoningStep(BaseModel):
    step_number: int
    thought: str
    tool: str
    tool_input: str
    observation: str

# --- Input Schemas ---
class UserRequest(BaseModel):
    query: str = Field(..., description="The main user task or question")
    session_id: str = Field(..., description="Unique ID for conversation context")
    output_format: OutputFormat = OutputFormat.MARKDOWN
    include_images: bool = False
    context_files: Optional[List[str]] = Field(default=None, description="Optional file content attached")

# --- Output Schemas ---
class AgentResponse(BaseModel):
    success: bool
    response_text: str
    sources: List[Source] = []
    reasoning_chain: List[ReasoningStep] = []
    execution_time_sec: float
    tokens_used: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
