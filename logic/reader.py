import feedparser
import time
import hashlib
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

def SanitizeFeed(feed):

    for entry in feed.entries:   

        print(feed.feed.get('title')) # RSS Feed Title , testing is Bleeping Computer
        print(entry.get('title')) # Article Titles

        cleanArticleLink = SanitizeURL(entry.get('link'))
        print(cleanArticleLink)
        
        if entry.get('published_parsed'):
            cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
        else:
            cleanDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        print(cleanDate)

        # get summary
        if entry.get('content'):
            print(entry.get('content'))
        elif entry.get('summary'):
            print(entry.get('summary'))
        else:
            print("No summary available")
            
        # I don't like when the ID is just the url, so taking the hash of the url instead
        guid = entry.get('id')
        if "https://" in guid:
            # feed is using link as guid, trust publisher
            print(hashlib.sha256(guid.encode('utf-8')).hexdigest())
        else:
            # feed is not, use our normalized/sanitized link
            print(hashlib.sha256(cleanArticleLink.encode('utf-8')).hexdigest())
        
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