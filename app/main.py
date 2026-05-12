from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
import sys
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import sqlite3
#sys.path.append(str(Path(__file__).parent.parent))
from db.connection import GetDBConnection
from logic.reader import UpdateAllFeeds, AddFeed, DeleteFeed



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

@scheduler.task('interval', id='do_update_feeds', minutes=15)
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

@app.route('/api/add-feed', methods=['GET', 'POST'])
def add_feed():
    #URL is sanitied in reader.py, should be safe to pass raw url through
    url = request.form.get('add-feed')
    status = AddFeed(url)
    # This can be improved later to prevent refreshing the whole page
    return redirect(url_for('index'))

# This should only exist in dev, a production environment probably shouldn't be deleting DB data from frontend
@app.route('/api/delete-feed', methods=['GET', 'POST'])
def delete_feed():
    feedID = request.form.get('feed-id')
    print(f"INFO: UI trying to delete feed {feedID}")
    status = DeleteFeed(feedID)
    print(f"Status: {status['status']}")
    return redirect(url_for('index'))
