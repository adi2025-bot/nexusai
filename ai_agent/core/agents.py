from groq import Groq
from ai_agent.core.prompts import PromptLibrary
from ai_agent.core.schemas import AgentRole
from ai_agent.config.settings import settings

class SpecializedAgent:
    def __init__(self, client: Groq, role: AgentRole, prompt: str):
        self.client = client
        self.role = role
        self.system_prompt = prompt

    async def process(self, task: str, context: str = "") -> str:
        """Executes a task within the persona's constraint."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nYour specific task:\n{task}"}
        ]
        response = self.client.chat.completions.create(
            model=settings.FAST_MODEL, 
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content

class AgentOrchestrator:
    """
    Manages the workflow. Delegates complex queries to ReAct engine or sub-agents.
    """
    def __init__(self, client: Groq):
        self.client = client
        self.researcher = SpecializedAgent(client, AgentRole.RESEARCHER, PromptLibrary.RESEARCHER_PROMPT)
        self.analyst = SpecializedAgent(client, AgentRole.ANALYST, PromptLibrary.ANALYST_PROMPT)
        self.critic = SpecializedAgent(client, AgentRole.CRITIC, PromptLibrary.CRITIC_PROMPT)

    async def run_research_pipeline(self, query: str, reasoning_engine) -> dict:
        print("🤖 Orchestrator: Initiating multi-agent research pipeline.")
        
        # 1. Researcher uses ReAct engine to gather data
        research_task = f"Research this thoroughly providing detailed facts and sources: {query}"
        research_result = await reasoning_engine.run(research_task, [])
        raw_data = research_result['response']
        chain = research_result['chain']

        # 2. Analyst synthesizes data
        print("🤖 Orchestrator: Handing off to Analyst.")
        analysis = await self.analyst.process(
            task="Synthesize the provided raw research into a coherent answer addressing the original query.",
            context=f"Original Query: {query}\n\nRaw Research:\n{raw_data}"
        )

        # 3. Critic reviews
        print("🤖 Orchestrator: Handing off to Critic for final review.")
        final_answer = await self.critic.process(
            task="Review the analysis for accuracy based on the raw data. Ensure it directly answers the prompt. Output the final version.",
            context=f"Original Query: {query}\n\nRaw Data Snippet: {raw_data[:500]}...\n\nProposed Analysis: {analysis}"
        )

        return {"response": final_answer, "chain": chain}
