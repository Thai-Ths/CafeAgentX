from datetime import datetime
from config import ALLOWED_AGENTS, INTAKE_PROMPT, RESPONSIBLITY

class IntakeAgent:
    def __init__(self, gemini_with_output, allowed_agents=None, intake_prompt=None):
        self.gemini_with_output = gemini_with_output
        self.allowed_agents = allowed_agents or ALLOWED_AGENTS
        self.intake_prompt = intake_prompt or INTAKE_PROMPT

    def build_messages(self, system_prompt: str, history: list, user_message: str) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt.strip()})
        if history:
            messages.extend(history)
        if user_message:
            messages.append({"role": "user", "content": user_message.strip()})
        return messages

    def validate_assignments(self, assignments, allowed_agents):
        errors = []
        for a in assignments:
            if a["agent"] not in allowed_agents:
                errors.append(f"[validate_assignments] Unknown agent: {a['agent']}")
        if errors:
            raise ValueError("\n".join(errors))

    @staticmethod
    def get_agent_capabilities(allowed_agents):
        return "\n".join([f"- {k}: {v['capability']}" for k, v in allowed_agents.items()])

    def process(self, state: dict) -> dict:
        # Build system prompt with date/time
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        allowed_agents = self.allowed_agents
        system_prompt = self.intake_prompt.format(
            responsibility=RESPONSIBLITY,
            Date_time=now,
            get_agent_capabilities=self.get_agent_capabilities(allowed_agents),
            agent_names=list(allowed_agents.keys())
        )

        user_message = state["user_message"]
        history = state["chat_history"]
        

        prompt = self.build_messages(system_prompt, history, user_message)

        gemini_result = self.gemini_with_output.invoke(prompt)
        assignments = gemini_result.get("assignments", [])

        self.validate_assignments(assignments, allowed_agents)

        is_finished = any(a.get("finish", False) for a in assignments)

        if is_finished:
            final_response = ""
            for a in assignments:
                if a.get("finish"):
                    final_response = a.get("command", "")
            assigned_agents = assignments
        else:
            final_response = ""
            assigned_agents = assignments

        log_msg = f"[{now}] [IntakeOfficer] input={user_message} assignments={assignments}"

        return {
        "assigned_agents": assigned_agents,
        "final_response": final_response,
        "logs": [log_msg]
        }
