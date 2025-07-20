from agents.base import BaseAgent
from datetime import datetime

class LanscapeCafeBot(BaseAgent):
    def __init__(self, rag_system, gemini_agent, system_prompt: str = None, top_k: int = 8):
        self.rag = rag_system
        self.gemini = gemini_agent
        self.top_k = top_k
        self.system_prompt = system_prompt or (
            "You are a helpful product support AI.\n"
            "- Answer user questions only using the reference context provided.\n"
            "- If the answer is not in the context, tell user that you do not have enough information.\n"
            "- Respond with clear and polite language. You may use emojis to enhance your response.\n"
            "- Do not include opinions, further explanations, or follow-up questions in your replies.\n"
            "- Always use the same language as the user."
        )

    def process(self, state: dict) -> dict:
        question = ""
        for a in state.get("assigned_agents", []):
            if a["agent"] == "landscape_cafe_bot":
                question = a["command"]
                break
        logs = []
        now = datetime.now().isoformat(timespec='seconds')
        logs.append(f"[{now}] [CafeBot] Received question: '{question}'")
        try:
            context = self.rag.query(question, top_k=self.top_k)
            logs.append(f"[{now}] [CafeBot] RAG context retrieved. Context length: {len(context)}")
        except Exception as e:
            logs.append(f"[{now}] [CafeBot][ERROR] Failed to retrieve context: {e}")
            return {"result": f"❌ Failed to retrieve reference context: {e}", "logs": logs}
        user_prompt = f"Reference context:\n{context}\n\nUser question: {question}"
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        try:
            answer = self.gemini.invoke(messages)
            result = answer.content if hasattr(answer, "content") else str(answer)
            logs.append(f"[{now}] [CafeBot] Gemini LLM returned answer. Length: {len(result)}")
        except Exception as e:
            logs.append(f"[{now}] [CafeBot][ERROR] Gemini LLM failed: {e}")
            return {"result": f"❌ Gemini LLM Error: {e}", "logs": logs}
        for a in state.get("assigned_agents", []):
            if a["agent"] == "landscape_cafe_bot":
                a["result"] = result
        logs.append(f"[{now}] [CafeBot] Result set in assigned_agents.")
        return {"logs": logs} 