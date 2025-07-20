import os
from config import settings
from config.agent_registry import AGENT_REGISTRY
from rag.rag_system import RAGSystem
from workflows.state import AssignmentResponse
from workflows.graph import build_workflow
from ui.app import create_app
import gradio as gr

# Import LLM (Gemini) and other dependencies as needed
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Initialize RAGSystem ONCE (global, not per chat) ---
rag = RAGSystem()  # Uses config.settings by default

# --- Factory functions for dependencies ---

def get_llm(api_key: str):
    """Create a Gemini LLM instance with the given API key."""
    return ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=api_key)

# --- Agent node wrappers for workflow ---

def make_agents(api_key: str, rag: RAGSystem):
    """
    Create agent node functions for the workflow, injecting dependencies.
    Returns a dict of node_name: callable(state) -> dict
    """
    llm = get_llm(api_key)
    # Intake agent expects a Gemini LLM with structured output
    intake_llm = llm.with_structured_output(AssignmentResponse)
    agents = {
        "intake_agent": AGENT_REGISTRY["intake_agent"](gemini_with_output=intake_llm),
        "landscape_cafe_bot": AGENT_REGISTRY["landscape_cafe_bot"](rag_system=rag, gemini_agent=llm),
        "coffee_db_agent": AGENT_REGISTRY["coffee_db_agent"](db_path=settings.DATABASE_PATH, llm_agent=llm),
        "aggregator_agent": AGENT_REGISTRY["aggregator_agent"](gemini_agent=llm),
    }
    # Wrap each agent as a node function for the workflow
    def node_wrapper(agent):
        def node_fn(state):
            return agent.process(state)
        return node_fn
    return {k: node_wrapper(v) for k, v in agents.items()}

# --- Workflow state and logic ---

def build_supportflowx_workflow(api_key: str, rag: RAGSystem):
    """
    Build the workflow graph with all agent nodes and dependencies.
    """
    agent_nodes = make_agents(api_key, rag)
    workflow = build_workflow(
        agent_nodes["intake_agent"],
        agent_nodes["landscape_cafe_bot"],
        agent_nodes["coffee_db_agent"],
        agent_nodes["aggregator_agent"]
    )
    return workflow

# --- Gradio Chat/Backend Logic ---

def chat(user_message: str, history: list = None, api_key: str = None):
    """
    Handle a chat message from the UI. Returns updated history and logs.
    """
    try:
        if not api_key or not api_key.startswith("AI"):
            return history or [], "⚠️ Please enter a valid Gemini API Key."
        if not user_message.strip():
            return history or [], "⚠️ Please fill in the message."
        # Build workflow for this session (could be cached per api_key)
        workflow = build_supportflowx_workflow(api_key, rag)
        allowed_agents = list(AGENT_REGISTRY.keys())
        chat_history = history.copy() if history else []
        state = {
            "user_message": user_message,
            "chat_history": chat_history,
            "allowed_agents": allowed_agents,
            "assigned_agents": {"assignments": []},
            "final_response": "",
            "logs": []
        }
        result = workflow.invoke(state)
        bot_reply = (result.get("final_response") or "Sorry, I did not understand your question. Please try again.")
        logs = "\n".join(result.get("logs", []))
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_reply})
        # Limit history to last 20 messages
        chat_history = chat_history[-20:]
        return chat_history, logs
    except Exception as e:
        return history or [], f"❌ Internal error: {str(e)[:500]}"

def clear_chat():
    """Clear the chat and logs."""
    return [], ""

# --- Main entry point ---
if __name__ == "__main__":
    # Optionally: sync database from CSVs on startup
    # csvs_to_sqlite()  # Uncomment if you want to auto-sync DB
    app = create_app(chat, clear_chat)
    app.launch(debug=settings.DEBUG) 