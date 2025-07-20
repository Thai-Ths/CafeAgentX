from typing import List, Dict, TypedDict
from typing_extensions import Annotated
import operator

# Represents a single agent assignment (for any agent, extensible)
class AgentAssignment(TypedDict):
    agent: str         # Agent name (e.g., "product_agent", "support_agent", ...)
    command: str       # Command or prompt for the agent
    result: str        # Result returned by the agent (optional, can be empty)
    finish: bool       # True if this assignment is a final/terminal response

# Represents a response containing multiple agent assignments
class AssignmentResponse(TypedDict):
    assignments: List[AgentAssignment]

# The main workflow state passed between nodes (extensible for new agents, logging, etc.)
class SupportFlowXState(TypedDict):
    user_message: str                      # Original user message
    chat_history: List[Dict[str, str]]     # Full chat history (user/agent)
    allowed_agents: List[str]              # List of allowed/registered agent names (can be extended)
    assigned_agents: AssignmentResponse    # List of agent assignments (for monitoring/debugging)
    final_response: str                    # Final response to the user (set/replace)
    logs: Annotated[List[str], operator.add]                    # System logs (append/add) 