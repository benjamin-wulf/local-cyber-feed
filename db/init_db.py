from pathlib import Path
import sqlite3

DB_FOLDER = Path(__file__).parent.absolute()
SCHEMA_PATH = DB_FOLDER / "schema.sql"
DATABASE_PATH = DB_FOLDER / "rss_reader.db"

def InitDB():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.execute("PRAGMA foreign_keys = ON")
        with open(SCHEMA_PATH) as f:
            connection.executescript(f.read())
        #connection.close()
        print(f"Database initialized at: {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    InitDB()