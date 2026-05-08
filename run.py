from app.main import app, scheduler
from db.init_db import InitDB, DB_FOLDER, DATABASE_PATH
from db.connection import GetDBConnection
from pathlib import Path
import os


#DB_FOLDER = Path(__file__).parent.absolute()
#SCHEMA_PATH = DB_FOLDER / "schema.sql"
#DATABASE_PATH = DB_FOLDER / "rss_reader.db"


if __name__ == "__main__":
    # Check if DB exists, if not then create it.
    print(f"Testing path: {DATABASE_PATH}")
    if not Path(DATABASE_PATH).exists():
        #db file does not exist, need to make
        print("INFO: Database file not found, attempting to create...")
        InitDB()
    else:
        #db file found, do nothing
        print("INFO: Found database file")
    # Launch the flask application
    #if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #    scheduler.start()
    #    print("INFO: Scheduler started in main worker process")

    #app.run(debug=True)