from flask import Flask, render_template
from flask_apscheduler import APScheduler
import sys
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.append(str(Path(__file__).parent.parent))
from db.connection import GetDBConnection
from logic.reader import UpdateAllFeeds

app = Flask(__name__)

@app.route('/')

def index():
    conn = GetDBConnection()
    
    feeds = conn.execute('SELECT * FROM feeds').fetchall()

    articles = conn.execute('SELECT a.title, a.link, a.published_date, f.title as feed_name FROM articles a JOIN feeds f ON a.feed_id = f.id ORDER BY a.published_date DESC LIMIT 10').fetchall()

    conn.close()
    #should have gotten feeds and 10 recent articles, now need to give the data to the HTML template
    return render_template('index.html', feeds=feeds, articles=articles)


scheduler = APScheduler()

@scheduler.task('interval', id='do_update_feeds', minutes=1)
def update_feeds_task():
    with app.app_context():
        print("Running background sync...")
        # fetch & update

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)