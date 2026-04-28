import sqlite3

def initDB():
    connection = sqlite3.connect('rss_reader.db')
    connection.execute("PRAGMA foreign_keys = ON")
    with open('./schema.sql') as f:
        connection.executescript(f.read())
    connection.close()

if __name__ == "__main__":
    initDB()
    print("Database Initialized")