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
    conn = GetDBConnection()
    
    feeds = conn.execute('SELECT * FROM feeds').fetchall()

    articles = conn.execute('SELECT a.title, a.link, a.published_date, a.added_at, f.title as feed_name FROM articles a JOIN feeds f ON a.feed_id = f.id ORDER BY a.published_date DESC LIMIT 10').fetchall()

    conn.close()
    #should have gotten feeds and 10 recent articles, now need to give the data to the HTML template
    return render_template('index.html', feeds=feeds, articles=articles)

@scheduler.task('interval', id='do_update_feeds', minutes=1)
def update_feeds_task():
    with app.app_context():
        print("Running background sync...")
        UpdateAllFeeds()
        # fetch & update

#@TODO: fix <int as it's receiving a string
@app.route('/api/check-updates/<int:last_time>')
def check_updates(last_time):
    try:
        conn = GetDBConnection()
        print("INFO: UI is checking for new articles")
        count = conn.execute('SELECT COUNT(*) FROM articles WHERE added_at >', (last_time)).fetchone()[0]
        return {"new_articles": count}
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()


#if __name__ == '__main__':
#    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#        scheduler.start()
#        print(" * Scheduler started in main worker process only")
#
#    app.run(debug=True)