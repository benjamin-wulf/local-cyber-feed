import feedparser
import time
import hashlib
import bleach
import re
from urllib.parse import urlparse, urlunparse


def FeedGrabber(url):
    feed = feedparser.parse(url)
    if (feed.bozo == 1):
        print("Failed to grab RSS feed.")
        return
    else:
        print("Successfuly grabbed RSS feed")
        #print(feed)
        cleanFeed = SanitizeFeed(feed)
        return cleanFeed

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

def main():
    testURL = "https://www.bleepingcomputer.com/feed/"
    cleanURL = SanitizeURL(testURL)
    testFeed = FeedGrabber(cleanURL)


if __name__ == "__main__":
    main()