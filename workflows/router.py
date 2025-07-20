from typing import List

# Router function to determine which agent(s) to activate next
# Returns a list of agent names to route to, or ["finish"] to end
# Extensible: If new agents are added to allowed_agents, they can be routed here

def intake_router(state: dict) -> List[str]:
    assignments = state.get("assigned_agents", [])
    assigned_names = [a["agent"] for a in assignments]
    # If any agent signals END, finish the workflow
    if "END" in assigned_names:
        return ["finish"]
    # Otherwise, route to all assigned agent names (can include new agents)
    return assigned_names 