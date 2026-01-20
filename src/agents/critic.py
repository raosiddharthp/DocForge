import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState

class ComplianceCritic:
    def __init__(self):
        # The Critic uses a standard temperature to ensure it catches errors reliably
        self.llm = ChatOllama(
            model="llama3", 
            temperature=0.1,
            base_url="http://localhost:11434",
            # AGGRESSIVE OPTIMIZATION:
            num_ctx=1024,
            num_thread=2,
            keep_alive="5m"
        )

    def review_draft(self, state: AgentState) -> dict:
        """
        Audits the draft for hallucinations and style violations.
        """
        print("   🧐  Critic is reviewing...")
        
        draft = state.get("current_draft", "")
        code_facts = state['code_context']
        
        # Serialize facts for the LLM
        facts_str = "\n".join([f"- Function: {c.name}\n  Signature: {c.signature}\n  Params: {c.parameters}" for c in code_facts])

        system_prompt = f"""You are the Compliance Auditor for Google Developer Documentation.
        Your job is to REJECT any draft that:
        1. Hallucinates parameters or return values not found in the Source of Truth.
        2. Uses passive voice (e.g., "is returned by").
        3. Uses vague words ("facilitate", "leverage").
        
        SOURCE OF TRUTH:
        {facts_str}
        
        INSTRUCTIONS:
        Return a JSON object with two keys:
        - "approved": boolean (true if perfect, false if ANY error exists)
        - "feedback": string (Explain the specific error if rejected. Say "LGTM" if approved.)
        """

        user_prompt = f"""
        AUDIT THIS DRAFT:
        {draft}
        
        Output JSON only.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Invoke LLM
        response = self.llm.invoke(messages)
        
        # Parse JSON output (LLMs sometimes add chatter, so we clean it)
        content = response.content.strip()
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            result = json.loads(json_str)
        except Exception as e:
            print(f"   ⚠️  Critic JSON Parse Error: {e}")
            return {
                "is_compliant": False, 
                "critique_feedback": "CRITICAL: Critic output was not valid JSON. Rejecting to be safe."
            }

        is_passing = result.get("approved", False)
        feedback = result.get("feedback", "Unknown error")

        if is_passing:
            print("   ✅  Draft Approved.")
        else:
            print(f"   ❌  Draft Rejected: {feedback}")

        return {
            "is_compliant": is_passing,
            "critique_feedback": feedback
        }