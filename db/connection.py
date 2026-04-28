import sqlite3
from pathlib import Path

DB_FOLDER = Path(__file__).parent.absolute()
DATABASE_PATH = DB_FOLDER / "rss_reader.db"

def GetDBConnection():

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        
        conn.execute("PRAGMA foreign_keys = ON")

        conn.row_factory = sqlite3.Row

        return conn
    
    except sqlite3.Error as e:
        print(f"ERROR: Failed to connect to database: {e}")
        return None