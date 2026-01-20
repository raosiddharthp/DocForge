import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState
from src.config.settings import load_config

# Hardcoded Style Guide for the MVP (Phase 1)
GOOGLE_STYLE_GUIDE = """
1. VOICE: Use active voice. (e.g., "The function returns..." NOT "The value is returned by...")
2. TENSE: Use present tense.
3. PERSON: Address the user as "you" (Second person).
4. CLARITY: Avoid vague words like "facilitate", "utilize", "leverage". Use "help", "use", "use".
5. PRECISION: Document parameters and return values exactly as they appear in the code.
"""

class StylistAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3", 
            temperature=0.2,
            base_url="http://localhost:11434",
            # AGGRESSIVE OPTIMIZATION: 
            # 1024 tokens is enough for a function doc, saves ~1GB RAM
            num_ctx=1024,
            # Limit to 2 threads so your OS has priority
            num_thread=2,
            keep_alive="5m"
        )

    def generate_draft(self, state: AgentState) -> dict:
        """
        The main node function for LangGraph.
        """
        print(f"   ✍️  Stylist is writing (Attempt {state.get('critique_count', 0) + 1})...")

        # 1. Prepare Context
        code_facts = state['code_context']
        # Convert Pydantic objects to a string representation for the LLM
        facts_str = "\n".join([f"- Function: {c.name}\n  Signature: {c.signature}\n  Docstring: {c.docstring}" for c in code_facts])
        
        previous_feedback = state.get('critique_feedback', None)
        feedback_instruction = ""
        if previous_feedback:
             feedback_instruction = f"\nCRITICAL INSTRUCTION: The previous draft was rejected. Fix these issues:\n{previous_feedback}"

        # 2. Build the Prompt
        system_prompt = f"""You are a Senior Technical Writer at Google. 
        Your goal is to write API documentation that strictly follows the Google Developer Style Guide.
        
        RULES:
        {GOOGLE_STYLE_GUIDE}
        
        SOURCE OF TRUTH (Do not hallucinate parameters):
        {facts_str}
        """

        user_prompt = f"""
        Write a reference documentation section for the functions listed in the Source of Truth.
        Include a description, parameters, and return values for each.
        {feedback_instruction}
        """

        # 3. Invoke LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # 4. Update State
        return {"current_draft": response.content}