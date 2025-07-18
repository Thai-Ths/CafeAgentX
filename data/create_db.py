import os
import glob
import pandas as pd
import sqlite3

def csvs_to_sqlite(csv_folder: str, db_path: str):
    """
    - Convert all CSV files in csv_folder to tables in SQLite DB at db_path.
    - If a CSV is updated, update table.
    - If a CSV is deleted, drop table in DB.
    - If a new CSV is added, create new table.
    """
    # 1. scan all csv files
    csv_files = {os.path.splitext(os.path.basename(f))[0]: f
                 for f in glob.glob(os.path.join(csv_folder, "*.csv"))}
    # 2. connect to db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. get existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = set(row[0] for row in cursor.fetchall())

    # 4. create/update tables from csv
    for table, file in csv_files.items():
        df = pd.read_csv(file)
        # Overwrite table (if exists) with current CSV
        df.to_sql(table, conn, if_exists='replace', index=False)
        print(f"[SYNC] Table '{table}' updated from {file}")

    # 5. drop tables that have no csv anymore
    for table in existing_tables:
        if table not in csv_files:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"[SYNC] Table '{table}' dropped (no CSV found)")

    conn.commit()
    conn.close()
    print("[SYNC] Database sync completed.")

# Example usage:
if __name__ == "__main__":
    csv_folder = "./My_project/SupportFlowX/data/raw"
    db_path = "./My_project/SupportFlowX/data//database.db"
    # os.makedirs("./data", exist_ok=True)
    csvs_to_sqlite(csv_folder, db_path)
