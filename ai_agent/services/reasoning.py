from groq import Groq
from ai_agent.core.prompts import PromptLibrary
from ai_agent.core.tools import ToolRegistry
from ai_agent.core.schemas import ReasoningStep
from ai_agent.config.settings import settings
import json
from datetime import date
import re
import asyncio

class ReActEngine:
    def __init__(self, client: Groq, tools: ToolRegistry):
        self.client = client
        self.tools = tools

    async def run(self, query: str, context_messages: list) -> dict:
        """Executes the ReAct loop: Thought -> Action -> Observation."""
        tool_names = self.tools.get_tool_names()
        system_prompt = PromptLibrary.CORE_SYSTEM_PROMPT.format(current_date=date.today())
        react_prompt = PromptLibrary.REACT_INSTRUCTIONS.format(tool_names=tool_names)
        
        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + react_prompt},
        ] + context_messages + [{"role": "user", "content": query}]

        reasoning_chain = []
        steps_taken = 0
        final_answer = ""

        while steps_taken < settings.MAX_REASONING_STEPS:
            # 1. Ask LLM for the next step
            try:
                # Groq call (Synchronous client wrapped in simple async logic if needed, 
                # but here we just call it directly as standard Groq client is sync.
                # Ideally we'd use AsyncGroq, but fitting to existing patterns/deps)
                completion = self.client.chat.completions.create(
                    model=settings.PRIMARY_MODEL,
                    messages=messages,
                    temperature=0.0,
                    stop=["Observation:"] 
                )
                content = completion.choices[0].message.content
                messages.append({"role": "assistant", "content": content})
                
                # 2. Parse Thought and Action
                thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|$)", content, re.DOTALL)
                action_match = re.search(r"Action:\s*(.+?)(?=\nAction Input:|$)", content, re.DOTALL)
                action_input_match = re.search(r"Action Input:\s*(.+?)(?=\n|$)", content, re.DOTALL)
                
                thought = thought_match.group(1).strip() if thought_match else ""
                
                if "Final Answer:" in content:
                    final_answer = content.split("Final Answer:")[1].strip()
                    return {"response": final_answer, "chain": reasoning_chain}

                if action_match and action_input_match:
                    tool_name = action_match.group(1).strip()
                    tool_input = action_input_match.group(1).strip()
                    
                    # 3. Execute Tool
                    observation = await self.tools.execute(tool_name, tool_input)
                    
                    # 4. Record step
                    reasoning_chain.append(ReasoningStep(
                        step_number=steps_taken + 1,
                        thought=thought,
                        tool=tool_name,
                        tool_input=tool_input,
                        observation=observation[:200] + "..." 
                    ))

                    # 5. Feed observation back to LLM
                    messages.append({"role": "user", "content": f"Observation: {observation}"})
                    steps_taken += 1
                else:
                    # If LLM doesn't call a tool but doesn't say "Final Answer", it might be chatting directly
                    if not "Action:" in content:
                         return {"response": content, "chain": reasoning_chain}
                    
                    steps_taken += 1
            except Exception as e:
                return {"response": f"Error in reasoning loop: {str(e)}", "chain": reasoning_chain}
                
        return {"response": "I reached my maximum reasoning steps without finding a final answer.", "chain": reasoning_chain}
