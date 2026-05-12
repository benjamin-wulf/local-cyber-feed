from flask import Flask, render_template
from flask_apscheduler import APScheduler
import sys
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import sqlite3
#sys.path.append(str(Path(__file__).parent.parent))
from db.connection import GetDBConnection
from logic.reader import UpdateAllFeeds



app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)

@app.route('/')
def index():

    try:
        conn = GetDBConnection()
        feeds = conn.execute('SELECT * FROM feeds').fetchall()
        articles = conn.execute('SELECT a.title, a.link, a.published_date, a.id, f.title as feed_name FROM articles a JOIN feeds f ON a.feed_id = f.id ORDER BY a.published_date DESC LIMIT 10').fetchall()
    except sqlite3.Error as e:
        print("ERROR: Could not read articles from DB: {e}")
    finally:
        conn.close()
    
    return render_template('index.html', feeds=feeds, articles=articles)

@scheduler.task('interval', id='do_update_feeds', minutes=1)
def update_feeds_task():
    with app.app_context():
        print("Running background sync...")
        UpdateAllFeeds()

@app.route('/api/check-updates/<string:last_id>')
def check_updates(last_id):
    print(f"Python received: {last_id}")
    try:
        conn = GetDBConnection()
        print("INFO: UI is checking for new articles")
        
        # This will likely need much more comprehensive checks when additional features are added
        # like users, sorting, and marking off read articles
        latestArticle = conn.execute('SELECT id FROM articles ORDER BY published_date DESC').fetchone()[0]

        if latestArticle == last_id:
            print("INFO: Told front end there is nothing new to display")
            return {"new_articles": 0}
        else:
            print("INFO: Told front end there is new content to display")
            return {"new_articles":1}
        
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()
