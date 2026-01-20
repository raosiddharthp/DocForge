import sys
import os

# Ensure we can import modules if run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# THE MEGA-PROMPT: All rules in one pass
REFINERY_SYSTEM_PROMPT = """
You are a Senior Technical Writer at Google.
Your goal is to rewrite legacy documentation to strictly adhere to the Google Developer Documentation Style Guide.

### CRITICAL RULES:
1. **Voice:** Use ACTIVE voice only. (Bad: "The button is clicked by the user." Good: "Click the button.")
2. **Tense:** Use PRESENT tense. (Bad: "The system will connect." Good: "The system connects.")
3. **Person:** Address the user as "you" (Second Person).
4. **Clarity:** Remove fluff. Delete words like "please", "kindly", "successfully", "in order to".
5. **Formatting:** Use Markdown. Use `code ticks` for technical terms, file paths, and variable names.
6. **Structure:** Keep headers but simplify the content below them.

### INSTRUCTION:
Rewrite the input text to be concise, clear, and compliant. 
Do NOT change the technical meaning. 
Do NOT add conversational filler ("Here is the rewritten text"). Just output the documentation.
"""

class RefineryAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3", 
            temperature=0, # ZERO for absolute determinism
            base_url="http://localhost:11434",
            num_ctx=2048,
            num_thread=2,
            keep_alive="5m"
        )

    def refine_chunk(self, text_chunk: str) -> str:
        """
        Rewrites a single chunk of text.
        """
        # If the chunk is just a header or very short, return as is to save LLM calls
        if len(text_chunk.strip()) < 10:
            return text_chunk

        messages = [
            SystemMessage(content=REFINERY_SYSTEM_PROMPT),
            HumanMessage(content=f"REWRITE THIS LEGACY TEXT:\n\n{text_chunk}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            # Fail safe: Return original text if LLM crashes
            print(f"⚠️ Refinery Error: {e}")
            return text_chunk

# --- VERIFICATION BLOCK ---
if __name__ == "__main__":
    print("🔥 Warming up the Refinery...")
    
    legacy_text = """
    ## User Login
    In order to access the system, the user is required to enter their credentials.
    It is recommended that the password field should be filled out by the user carefully.
    Upon successful completion, the system will redirect you to the dashboard.
    """
    
    agent = RefineryAgent()
    result = agent.refine_chunk(legacy_text)
    
    print("\n--- BEFORE ---")
    print(legacy_text.strip())
    print("\n--- AFTER (Google Style) ---")
    print(result)