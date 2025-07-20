from agents.base import BaseAgent
import sqlite3
import pandas as pd
from datetime import datetime
import re

class CoffeeDatabaseAgent(BaseAgent):
    def __init__(self, db_path: str, llm_agent):
        self.db_path = db_path
        self.llm_agent = llm_agent

    def check_connection(self) -> bool:
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
        if hasattr(response, 'content'):
            sql = response.content
        else:
            sql = str(response)
        match = re.search(r"```sql\s*(.*?)```", sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
        elif sql.startswith("```") and sql.endswith("```"):
            sql = sql[3:-3].strip()
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

    def process(self, state: dict) -> dict:
        command = ""
        for a in state.get("assigned_agents", []):
            if a["agent"] == "coffee_db_agent":
                command = a["command"]
                break
        logs = []
        now = datetime.now().isoformat(timespec='seconds')
        logs.append(f"[{now}] [DatabaseAgent] Received command: '{command}'")
        if not self.check_connection():
            log = f"[{now}] [DatabaseAgent][ERROR] Cannot connect to database ({self.db_path})"
            return {"result": "❌ Database connection failed.", "logs": [log]}
        schema = self.get_schema_overview()
        logs.append(f"[{now}] [DatabaseAgent] Schema overview: {schema}")
        try:
            sql = self.llm_to_sql(command, schema)
            logs.append(f"[{now}] [DatabaseAgent] LLM generated SQL: {sql}")
        except Exception as e:
            log = f"[{now}] [DatabaseAgent][ERROR] LLM to SQL failed: {e}"
            return {"result": f"❌ [LLM Error]: {e}", "logs": logs + [log]}
        try:
            df = self.query_database(sql)
            if df.empty:
                result = "No data found for your request."
            else:
                result = f"Query result:\n{df.to_string(index=False)}"
            logs.append(f"[{now}] [DatabaseAgent] Query executed successfully. Rows: {len(df)}")
        except Exception as e:
            result = f"❌ [DB Error]: {e}\n(SQL: {sql})"
            logs.append(f"[{now}] [DatabaseAgent][ERROR] Query execution failed: {e}")
        logs.append(f"[{now}] [DatabaseAgent] Done. Result set in assigned_agents.")
        for a in state.get("assigned_agents", []):
            if a["agent"] == "coffee_db_agent":
                a["result"] = result
        return {"logs": logs}



