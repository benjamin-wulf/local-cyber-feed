import feedparser
import time
import hashlib
import bleach
import re
import sqlite3
from urllib.parse import urlparse, urlunparse
from db.connection import GetDBConnection


def FeedGrabber(url):
    feed = feedparser.parse(url)
    if (feed.bozo == 1):
        print("Failed to grab RSS feed.")
        return
    else:
        print("Successfuly grabbed RSS feed")
        #print(feed)
        # cleanFeed = SanitizeFeed(feed)
        return feed

# Fully stripping ALL parameters may break some sites
def SanitizeURL(dirtyURL):

    parsedURL = urlparse(dirtyURL)
    
    cleanURL = urlunparse((parsedURL.scheme, parsedURL.netloc, parsedURL.path, '', '', ''))
    cleanURL = cleanURL.rstrip('/')

    # set url to lowercase
    cleanURL = cleanURL.lower()

    return cleanURL

def SanitizeContent(rawContent):
    # strip tags: <script>, <style>, <iframe>, <embed>, <object>, <form>, <meta>
    # strip attributes: onclick, onload, onerror, style

    # can keep: <p>, <br>, <ul>, <ol>, <li>, <blockquote>
    # formatting: <b>, <strong>, <i>, <em>, <u>
    # links: <a> (but force target="_blank" AND rel="noopener noreferrer")

    # decide how to handle <img> later

    allowedTags = ['p', 'b', 'i', 'strong', 'em', 'a', 'ul', 'ol', 'li', 'br', 'blockquote']
    allowedAttributes = {
        'a': ['href', 'title', 'rel'],
        'img': ['src', 'alt', 'title']
    }

    # might make sentences at the end of paragraphs clash without a space. "BeautifulSoup" package is an option, or replace </p> maybe?
    cleanContent = bleach.clean(rawContent, tags=allowedTags, attributes=allowedAttributes, strip=True, strip_comments=True)

    #print("CLEAN CONTENT: " + cleanContent)
    return cleanContent

# if the feed is only supplying a brief summary, this may not always detect updates
def GetContentHash(rawContent):

    ultraCleanContent = bleach.clean(rawContent, tags=[], strip=True, strip_comments=True)
    ultraCleanContent = ultraCleanContent.lower()

    # regex is probably overkill for this but who cares
    ultraCleanContent = re.sub(r"\s+", "", ultraCleanContent)

    contentHash = hashlib.sha256(ultraCleanContent.encode('utf-8')).hexdigest()
    return contentHash

def SanitizeFeed(feed):

    for entry in feed.entries:   

        print("RSS Feed Title: " + feed.feed.get('title')) # RSS Feed Title , testing is Bleeping Computer
        print("Article Title: " + entry.get('title')) # Article Titles

        cleanArticleLink = SanitizeURL(entry.get('link'))
        print("Clean Article Link: " + cleanArticleLink)
        
        if entry.get('published_parsed'):
            cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
        else:
            cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        print("Date: " + cleanDate)

        # get summary
        rawContent = ""
        if entry.get('content'):
            rawContent = entry.get('content')
        elif entry.get('summary'):
            rawContent = entry.get('summary')
        else:
            rawContent = "No summary available."

        print("Cleaned Content is: " + SanitizeContent(rawContent))
        print("Content Hash is: " + GetContentHash(rawContent))
            
        # I don't like when the ID is just the url, so taking the hash of the url instead
        if entry.get('guidislink'):
            # feed is using link as guid, trust publisher
            print("Hashed ID is: " + hashlib.sha256(entry.guid.encode('utf-8')).hexdigest())
        elif all([urlparse(entry.guid).scheme in ['http', 'https'], urlparse(entry.guid).netloc]):
            # feed doesn't have guidislink set, but guid does appear to be a link
            print("Hashed ID is: " + hashlib.sha256(entry.guid.encode('utf-8')).hexdigest())
        else:
            # just use our cleaned article link
            print("Hashed ID is: " + hashlib.sha256(cleanArticleLink.encode('utf-8')).hexdigest())
        
        print("\n")

        # @TODO: load all cleaned/sanitized data into a dict to return later
        #sanitized = {
            #"feedTitle": feed.get('title')
        #}

    # @TODO: This is currently returning the original input while testing, change to cleaned/sanitized once it exists
    return feed

def AddFeed(rawURL):

    cleanURL = SanitizeURL(rawURL)

    conn = GetDBConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM feeds WHERE url = ?", (cleanURL,))

    feedExists = cursor.fetchone()

    if feedExists:
        conn.close()
        return {"status": "exists", "feed_id": feedExists[0] }
    
    feed = FeedGrabber(cleanURL)

    if feed.bozo:
        conn.close()
        return {"status": "error", "message": "Could not retrieve RSS feed" }
    
    # if we're here, the feed does not exist in the db AND we were able to grab the feed

    feedTitle = feed.feed.get('title', cleanURL)

    try:
        cursor.execute(
            "INSERT INTO feeds (url, title) VALUES (?, ?)",
            (cleanURL, feedTitle)
        )
        feedID = cursor.lastrowid

        #TODO: Clean up a lot of the retrieval by breaking into separate functions
        for entry in feed.entries:
            # need unique id (guid/link/sha256 hash of link) feed_id, article title, clean link, published date, summary, content hash 

            articleTitle = entry.get('title')
            cleanArticleLink = SanitizeURL(entry.get('link'))
            
            if entry.get('published_parsed'):
                cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
            else:
                cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            
            rawContent = ""
            if entry.get('content'):
                rawContent = entry.get('content')
            elif entry.get('summary'):
                rawContent = entry.get('summary')
            else:
                rawContent = "No summary available."

            cleanContent = SanitizeContent(rawContent)
            contentHash = GetContentHash(rawContent)
                
            # I don't like when the ID is just the url, so taking the hash of the url instead
            if entry.get('guidislink'):
                # feed is using link as guid, trust publisher
                articleHashID = hashlib.sha256(entry.guid.encode('utf-8')).hexdigest()
            elif all([urlparse(entry.guid).scheme in ['http', 'https'], urlparse(entry.guid).netloc]):
                # feed doesn't have guidislink set, but guid does appear to be a link
                articleHashID = hashlib.sha256(entry.guid.encode('utf-8')).hexdigest()
            else:
                # just use our cleaned article link
                articleHashID = hashlib.sha256(cleanArticleLink.encode('utf-8')).hexdigest()

            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (id, feed_id, title, link, published_date, summary, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (articleHashID, feedID, articleTitle, cleanArticleLink, cleanDate, cleanContent, contentHash))
        
        conn.commit()
        return {"status":"success", "feed_id": feedID}
        
    except sqlite3.Error as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

# Will need to implement a "GetFeedID function"
def DeleteFeed(feedID):

    conn = GetDBConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM feeds WHERE id = ?", (feedID,))

    feedExists = cursor.fetchone()

    if feedExists:
        #delete feed and related articles
        try:
            cursor.execute("DELETE FROM feeds WHERE id = ?", (feedID,))
            
            # db should automatically wipe articles associated with this feedID
            #cursor.execute("DELETE FROM articles WHERE feed_id = ?", (feedID,))
            
            conn.commit()
            return {"status":"successfully deleted feed", "feed_id": feedID}
        except sqlite3.Error as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()

    else:
        #feed doesn't exist
        return {"status": "feed not found in db"}


def main():
    testURL = "https://www.bleepingcomputer.com/feed/"
    #cleanURL = SanitizeURL(testURL)
    #testFeed = FeedGrabber(cleanURL)
    
    # can put the raw url straight in, it gets sanitized in AddFeed()
    
    result = AddFeed(testURL)
    print(f"Status: {result['status']} with feed ID: {result['feed_id']}")

    #result = DeleteFeed(4)
    #print(f"Status: {result['status']} with feed ID: {result['feed_id']}")


if __name__ == "__main__":
    main()