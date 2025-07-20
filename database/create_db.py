import os
import glob
import pandas as pd
import sqlite3
from config import settings

def csvs_to_sqlite(csv_folder: str = None, db_path: str = None):
    """
    Convert all CSV files in csv_folder to tables in SQLite DB at db_path.
    - If a CSV is updated, update table.
    - If a CSV is deleted, drop table in DB.
    - If a new CSV is added, create new table.
    Paths are configurable via config.settings.
    """
    # Use config if not provided
    csv_folder = str(csv_folder or (settings.ASSETS_DIR / "raw_data"))
    db_path = str(db_path or settings.DATABASE_PATH)

    # 1. Scan all csv files in the folder
    csv_files = {os.path.splitext(os.path.basename(f))[0]: f
                 for f in glob.glob(os.path.join(csv_folder, "*.csv"))}
    # 2. Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. Get existing tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = set(row[0] for row in cursor.fetchall())

    # 4. Create/update tables from CSV files
    for table, file in csv_files.items():
        df = pd.read_csv(file)
        # Overwrite table (if exists) with current CSV
        df.to_sql(table, conn, if_exists='replace', index=False)
        print(f"[DB SYNC] Table '{table}' updated from {file}")

    # 5. Drop tables that have no corresponding CSV anymore
    for table in existing_tables:
        if table not in csv_files:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"[DB SYNC] Table '{table}' dropped (no CSV found)")

    conn.commit()
    conn.close()
    print("[DB SYNC] Database sync completed.")

if __name__ == "__main__":
    csvs_to_sqlite()
