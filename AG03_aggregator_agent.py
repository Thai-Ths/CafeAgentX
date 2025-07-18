from datetime import datetime

class AggregatorAgent:
    def __init__(self, gemini_agent):
        self.gemini = gemini_agent

    def summarize_database_output(self, table_text, user_message):

        prompt = (
            "You are a helpful and friendly assistant. Organize and present the following database table for the user in a clear, concise, and visually appealing summary. "
            "Use bullet points, short tables, or lists if helpful, and add emojis to enhance readability where appropriate. "
            "Focus only on answering the user's request; do not add extra information. "
            "If the table is empty, reply with a polite message that no data was found. "
            "Always answer in the exact same language as the user's question.\n\n"
            f"User question: {user_message}\n"
            f"Database output:\n{table_text}\n"
        )
        result = self.gemini.invoke([{"role": "user", "content": prompt}])
        return result.content if hasattr(result, "content") else str(result)

    def summarize_multiple_agents(self, agent_outputs, user_message):

        prompt = (
            "You are a helpful and friendly assistant. The following are responses from multiple support agents to the same user query. "
            "Please combine, reorganize, and summarize all relevant information into a single, concise, and easy-to-read reply for the user. "
            "Remove any duplicate or redundant details. Use a friendly tone, and you may add emojis to make the message more engaging. "
            "If there are conflicting answers, use the most accurate or comprehensive information.\n\n"
            "Always answer in the exact same language as the user's question.\n"
            f"User question: {user_message}\n"
            "Agent outputs:\n"
        )
        for label, text in agent_outputs:
            prompt += f"[{label}]: {text}\n"
        result = self.gemini.invoke([{"role": "user", "content": prompt}])
        return result.content if hasattr(result, "content") else str(result)

    def process(self, state: dict) -> dict:
        assigned_agents = state.get("assigned_agents", [])
        user_message = state.get("user_message", "")
        log_msg = []
        now = datetime.now().isoformat(timespec='seconds')

        # 1. ตรวจว่ายังมี agent ไหนที่ยังไม่ได้ result หรือไม่
        waiting = [a["agent"] for a in assigned_agents if not a.get("result")]
        if waiting:
            log_msg.append(f"[{now}] [AGGREGATOR]: Waiting for {waiting} ...")
            return {"logs": log_msg}

        # 2. ถ้ามี agent เดียว (ไม่ใช่ coffee_db_agent) → return result เดิม
        if len(assigned_agents) == 1:
            agent = assigned_agents[0]["agent"]
            result = assigned_agents[0].get("result", "")
            if agent != "coffee_db_agent":
                log_msg.append(f"[{now}] [AGGREGATOR]: Single agent, pass through.")
                return {"final_response": result, "logs": log_msg}

            # ถ้าเป็น coffee_db_agent, สรุป output
            summary = self.summarize_database_output(result, user_message)
            log_msg.append(f"[{now}] [AGGREGATOR]: Summarized database output.")
            return {"final_response": summary, "logs": log_msg}

        # 3. ถ้ามีหลาย agent: รวมผลลัพธ์ทุก agent แล้ว summarize ด้วย LLM
        agent_outputs = []
        for a in assigned_agents:
            agent = a["agent"]
            result = a.get("result", "")
            if result:
                agent_outputs.append((agent, result))
        summary = self.summarize_multiple_agents(agent_outputs, user_message)
        log_msg.append(f"[{now}] [AGGREGATOR]: Summarized multi-agent output.")
        return {"final_response": summary.strip(), "logs": log_msg}