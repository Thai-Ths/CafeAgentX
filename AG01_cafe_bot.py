from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from RAG import RAGSystem
import os
from datetime import datetime

class LanscapeCafeBot:
    def __init__(
        self,
        rag_system,
        gemini_agent,
        system_prompt: str = None,
        top_k: int = 8,
    ):
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

    def process(self, question: str) -> dict:
        logs = []
        now = datetime.now().isoformat(timespec='seconds')
        try:
            # 1. Retrieve context from RAG
            context = self.rag.query(question, top_k=self.top_k)
            logs.append(f"[{now}] [ProductAgent] RAG context retrieved.")
        except Exception as e:
            logs.append(f"[{now}] [ProductAgent][ERROR] Failed to retrieve context: {e}")
            return {"result": f"❌ Failed to retrieve reference context: {e}", "logs": self.format_logs(logs)}
        # 2. Build message for Gemini
        user_prompt = f"Reference context:\n{context}\n\nUser question: {question}"
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        try:
            answer = self.gemini.invoke(messages)
            result = answer.content if hasattr(answer, "content") else str(answer)
            logs.append(f"[{now}] [ProductAgent] Gemini answered.")
        except Exception as e:
            logs.append(f"[{now}] [ProductAgent][ERROR] Gemini LLM failed: {e}")
            return {"result": f"❌ Gemini LLM Error: {e}", "logs": self.format_logs(logs)}
        return {"result": result, "logs": self.format_logs(logs)}

    @staticmethod
    def format_logs(logs):
        # Remove leading/trailing whitespace and join with line breaks
        return [log.strip() for log in logs if log.strip()]


if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    knowledge_base_path = os.path.join(BASE_DIR, "knowledge-base")
    db_path = os.path.join(BASE_DIR, "supportflowx_db")

    print("Current working directory:", db_path)

    rag = RAGSystem(
        knowledge_base_path=knowledge_base_path,
        collection_name="knowledge_BAAI",
        chunk_size=1000,
        chunk_overlap=200,
        db_path=db_path,
        embedding_model_name="BAAI/bge-m3"
    )

    load_dotenv(override=True)
    gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")

    agent = LanscapeCafeBot(rag, gemini)
    output = agent.process("เกี่ยวกับบริษัท")
    print(output["result"])