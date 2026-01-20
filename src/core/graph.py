from langgraph.graph import StateGraph, END
from src.core.state import AgentState
from src.agents.stylist import StylistAgent
from src.agents.critic import ComplianceCritic

# Initialize Agents
stylist = StylistAgent()
critic = ComplianceCritic()

def stylist_node(state: AgentState):
    """
    Invokes the Google Stylist agent.
    """
    result = stylist.generate_draft(state)
    return {
        "current_draft": result["current_draft"],
        "critique_count": state.get("critique_count", 0) # Count stays same here
    }

def critic_node(state: AgentState):
    """
    Invokes the Compliance Critic agent.
    """
    result = critic.review_draft(state)
    return {
        "is_compliant": result["is_compliant"],
        "critique_feedback": result["critique_feedback"],
        "critique_count": state.get("critique_count", 0) + 1 # Increment loop count
    }

def should_continue(state: AgentState):
    """
    Conditional Logic: Should we loop or end?
    """
    if state["is_compliant"]:
        return "end"
    
    if state["critique_count"] >= state["max_revisions"]:
        print("   ⚠️  Max revisions reached. Stopping loop.")
        return "end"
    
    return "retry"

# --- Build the Graph ---
workflow = StateGraph(AgentState)

# 1. Add Nodes
workflow.add_node("stylist", stylist_node)
workflow.add_node("critic", critic_node)

# 2. Define Entry Point
workflow.set_entry_point("stylist")

# 3. Define Edges
workflow.add_edge("stylist", "critic")

# 4. Define Conditional Edge (The Loop)
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "retry": "stylist",
        "end": END
    }
)

# 5. Compile
app = workflow.compile()

# Self-Test
if __name__ == "__main__":
    from src.db.schema import CodeEntity, SourceMetadata
    
    # Mock Data (A messy function signature)
    meta = SourceMetadata(source_file="auth.py", source_type="code", line_number=10)
    mock_code = [
        CodeEntity(
            name="process_payment", 
            entity_type="function", 
            signature="def process_payment(amt: float, ccy: str, force: bool = False)",
            parameters={"raw": "(amt: float, ccy: str, force: bool = False)"},
            metadata=meta
        )
    ]

    initial_state = AgentState(
        project_name="Demo Run",
        target_file="auth.py",
        code_context=mock_code,
        doc_requirements=[],
        drift_report={},
        critique_count=0,
        max_revisions=3,
        current_draft="",
        critique_feedback=None,
        is_compliant=False
    )

    print("\n🚀 Starting DocForge Logic Swarm...\n")
    final_state = app.invoke(initial_state)
    
    print("\n🏁 Final Output:\n")
    print(final_state["current_draft"])