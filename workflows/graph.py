from langgraph.graph import StateGraph, END
from workflows.state import SupportFlowXState
from workflows.router import intake_router

# Build the workflow graph for SupportFlowX
# To add a new agent:
#   1. Add a node with graph.add_node("agent_name", agent_node_fn)
#   2. Add routing logic in intake_router and conditional_edges
#   3. Add edges as needed for the workflow

def build_workflow(intake_node, landscape_cafe_bot, coffee_db_agent, aggregator_node, **extra_agents):
    graph = StateGraph(SupportFlowXState)
    # Add core agent nodes
    graph.add_node("intake_agent", intake_node)
    graph.add_node("landscape_cafe_bot", landscape_cafe_bot)
    graph.add_node("coffee_db_agent", coffee_db_agent)
    graph.add_node("aggregator", aggregator_node)
    # Add extra agent nodes dynamically (for extensibility)
    for agent_name, agent_fn in extra_agents.items():
        graph.add_node(agent_name, agent_fn)
    graph.set_entry_point("intake_agent")

    # Conditional routing from intake_agent to assigned agents or finish
    graph.add_conditional_edges(
        "intake_agent",
        intake_router,
        {
            "landscape_cafe_bot": "landscape_cafe_bot",
            "coffee_db_agent": "coffee_db_agent",
            # Add new agent routing here as needed
            "finish": END,
        }
    )
    # Edges from agent nodes to aggregator (or other nodes as needed)
    graph.add_edge("landscape_cafe_bot", "aggregator")
    graph.add_edge("coffee_db_agent", "aggregator")
    # Add edges for extra agents to aggregator (or other nodes)
    for agent_name in extra_agents:
        graph.add_edge(agent_name, "aggregator")
    graph.add_edge("aggregator", END)
    return graph.compile() 