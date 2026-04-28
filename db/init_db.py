from pathlib import Path
import sqlite3

DB_FOLDER = Path(__file__).parent.absolute()
SCHEMA_PATH = DB_FOLDER / "schema.sql"
DATABASE_PATH = DB_FOLDER / "rss_reader.db"

def initDB():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH) as f:
        connection.executescript(f.read())
    connection.close()
    print(f"Database initialized at: {DATABASE_PATH}")

if __name__ == "__main__":
    initDB()