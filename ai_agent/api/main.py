from fastapi import FastAPI, HTTPException, BackgroundTasks
from groq import Groq
import time
import os

from ai_agent.config.settings import settings
from ai_agent.core.schemas import UserRequest, AgentResponse
from ai_agent.core.tools import ToolRegistry
from ai_agent.core.memory import MemoryManager
from ai_agent.core.agents import AgentOrchestrator
from ai_agent.services.reasoning import ReActEngine
from ai_agent.services.output_formatter import OutputFormatter

app = FastAPI(title="Atlas AI Agent API", version="1.0")

# --- Dependency Injection Setup ---
if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

groq_client = Groq(api_key=settings.GROQ_API_KEY)
tools = ToolRegistry()
memory = MemoryManager()
orchestrator = AgentOrchestrator(groq_client)
react_engine = ReActEngine(groq_client, tools)

print("[SYSTEM] Atlas Agent API Initialized")

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    try:
        # 1. Retrieve Context
        short_term_history = memory.get_recent_context(request.session_id)
        
        # 2. Determine Execution Strategy
        # Simple heuristic: > 15 words or "research" keyword = Complex
        is_complex_task = len(request.query.split()) > 15 or "research" in request.query.lower()

        if is_complex_task:
             result = await orchestrator.run_research_pipeline(request.query, react_engine)
        else:
             # Simple ReAct run
             result = await react_engine.run(request.query, short_term_history)

        response_text = result['response']
        reasoning_chain = result['chain']

        # 3. Format Output & Extract Sources
        cleaned_text, sources = OutputFormatter.extract_sources(response_text)
        
        # 4. Update Memory
        background_tasks.add_task(memory.add_interaction, request.session_id, "user", request.query)
        background_tasks.add_task(memory.add_interaction, request.session_id, "assistant", cleaned_text)

        execution_time = time.time() - start_time

        return AgentResponse(
            success=True,
            response_text=cleaned_text,
            sources=sources,
            reasoning_chain=reasoning_chain,
            execution_time_sec=execution_time,
            tokens_used=0 
        )

    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "operational", "agent": "Atlas", "model": settings.PRIMARY_MODEL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
