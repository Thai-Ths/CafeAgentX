import sqlite3
import pandas as pd
from datetime import datetime
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

class CoffeeDatabaseAgent:
    def __init__(self, db_path: str, llm_agent):
        import os
        # Make db_path dynamic if relative
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
        self.llm_agent = llm_agent

    def check_connection(self) -> bool:
        """ตรวจสอบว่าเชื่อมต่อ database ได้หรือไม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1;")
            conn.close()
            return True
        except Exception as e:
            print(f"[DatabaseAgent] DB Connection Error: {e}")
            return False

    def get_schema_overview(self) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if not tables:
                return "(No tables found)"
            lines = []
            for (table,) in tables:
                columns = cursor.execute(f"PRAGMA table_info({table})").fetchall()
                col_list = [col[1] for col in columns]
                col_meta = []
                for col in col_list:
                    # หา unique values ถ้า columns ที่ชื่อเหมือน enum/category/status/type
                    if any(kw in col.lower() for kw in ["status", "type", "category", "state", "flag"]):
                        vals = cursor.execute(f"SELECT DISTINCT {col} FROM {table} LIMIT 21").fetchall()
                        vals = [str(v[0]) for v in vals if v[0] is not None]
                        if 1 < len(vals) <= 20:
                            col_meta.append(f"{col}: [{', '.join(vals)}]")
                if col_meta:
                    lines.append(f"{table}({', '.join(col_list)})  # " + "; ".join(col_meta))
                else:
                    lines.append(f"{table}({', '.join(col_list)})")
            conn.close()
            return "\n".join(lines)
        except Exception as e:
            return f"(Schema error: {e})"

    def llm_to_sql(self, command: str, schema: str) -> str:
        prompt = (
            "You are a database specialist agent. Given the schema and user request, generate a single, safe SQL SELECT statement. "
            "If you cannot answer with available tables/columns, reply NO_SQL.\n"
            f"Database schema overview:\n{schema}\n"
            f"User request: {command}\nSQL:"
        )
        response = self.llm_agent.invoke([{"role": "user", "content": prompt}])
        
        # แปลง response เป็น string ถ้าเป็น object
        if hasattr(response, 'content'):
            sql = response.content
        else:
            sql = str(response)
        
        # 1. หา ```sql ... ```
        match = re.search(r"```sql\s*(.*?)```", sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
        # 2. หรือถ้ามี ``` ... ```
        elif sql.startswith("```") and sql.endswith("```"):
            sql = sql[3:-3].strip()
        # 3. หรือถ้า LLM ตอบ SQL: ... 
        elif sql.upper().startswith("SQL:"):
            sql = sql[4:].strip()
        
        return sql

    def query_database(self, sql: str, max_rows: int = 15) -> pd.DataFrame:
        if sql.upper() == "NO_SQL":
            raise ValueError("Cannot answer this question with the given schema.")
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn)
        finally:
            conn.close()
        return df.head(max_rows)

    def process(self, command: str) -> dict:
        logs = []
        now = datetime.now().isoformat(timespec='seconds')

        # 1. Check DB connection
        if not self.check_connection():
            log = f"[{now}] [DatabaseAgent] ERROR: Cannot connect to database ({self.db_path})"
            return {"result": "❌ Database connection failed.", "logs": self.format_logs([log])}

        # 2. Get schema
        schema = self.get_schema_overview()
        logs.append(f"[{now}] [DatabaseAgent] Schema: {schema}")

        # 3. LLM → SQL
        try:
            sql = self.llm_to_sql(command, schema)
            logs.append(f"[{now}] [DatabaseAgent] SQL: {sql}")
            print(f"[SQL]: {sql}")
        except Exception as e:
            log = f"[{now}] [DatabaseAgent] LLM Error: {e}"
            return {"result": f"❌ [LLM Error]: {e}", "logs": self.format_logs(logs + [log])}

        # 4. Query DB
        try:
            df = self.query_database(sql)
            if df.empty:
                result = "No data found for your request."
            else:
                result = f"Query result:\n{df.to_string(index=False)}"
        except Exception as e:
            # Safe to reference `sql` here because it's guaranteed to exist
            result = f"❌ [DB Error]: {e}\n(SQL: {sql})"

        logs.append(f"[{now}] [DatabaseAgent] Done.")
        return {"result": result, "logs": self.format_logs(logs)}

    @staticmethod
    def format_logs(logs):
        return [log.strip() for log in logs if log.strip()]
    
if __name__ == "__main__":
    load_dotenv(override=True)
    gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "data", "database.db")
    agent = CoffeeDatabaseAgent(db_path=db_path, llm_agent=gemini)
    output = agent.process("สินค้าขายดี")
    print(output["result"])
    for log in output["logs"]:
        print(log)