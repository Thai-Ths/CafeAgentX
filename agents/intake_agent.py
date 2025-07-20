from agents.base import BaseAgent
from datetime import datetime
from config.config import ALLOWED_AGENTS, INTAKE_PROMPT, RESPONSIBLITY

class IntakeAgent(BaseAgent):
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
                errors.append(f"[IntakeAgent] Unknown agent assigned: {a['agent']}")
        if errors:
            raise ValueError("\n".join(errors))

    @staticmethod
    def get_agent_capabilities(allowed_agents):
        return "\n".join([f"- {k}: {v['capability']}" for k, v in allowed_agents.items()])

    def process(self, state: dict) -> dict:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        allowed_agents = self.allowed_agents
        system_prompt = self.intake_prompt.format(
            responsibility=RESPONSIBLITY,
            Date_time=now,
            get_agent_capabilities=self.get_agent_capabilities(allowed_agents),
            agent_names=list(allowed_agents.keys())
        )
        user_message = state.get("user_message", "")
        history = state.get("chat_history", [])
        logs = []
        logs.append(f"[{now}] [IntakeAgent] Received user message: '{user_message}'")
        prompt = self.build_messages(system_prompt, history, user_message)
        logs.append(f"[{now}] [IntakeAgent] Built prompt for LLM. History count: {len(history)}")
        try:
            gemini_result = self.gemini_with_output.invoke(prompt)
            assignments = gemini_result.get("assignments", [])
            logs.append(f"[{now}] [IntakeAgent] LLM returned assignments: {assignments}")
            self.validate_assignments(assignments, allowed_agents)
        except Exception as e:
            logs.append(f"[{now}] [IntakeAgent][ERROR] LLM or assignment validation failed: {e}")
            return {"assigned_agents": [], "final_response": "", "logs": logs}
        is_finished = any(a.get("finish", False) for a in assignments)
        final_response = ""
        if is_finished:
            for a in assignments:
                if a.get("finish"):
                    final_response = a.get("command", "")
            logs.append(f"[{now}] [IntakeAgent] Conversation finished. Final response: '{final_response}'")
        else:
            logs.append(f"[{now}] [IntakeAgent] Assignments sent to next agent(s): {[a['agent'] for a in assignments]}")
        return {
            "assigned_agents": assignments,
            "final_response": final_response,
            "logs": logs
        }



