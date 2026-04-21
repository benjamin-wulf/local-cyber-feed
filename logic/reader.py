import feedparser
import time
import hashlib


def FeedGrabber(url):
    feed = feedparser.parse(url)
    if (feed.bozo == 1):
        print("Failed to grab RSS feed.")
        return
    else:
        print("Successfuly grabbed RSS feed")
        cleanFeed = SanitizeFeed(feed)
        return cleanFeed

def SanitizeFeed(feed):

    for entry in feed.entries:        
        print(feed.feed.get('title')) # RSS Feed Title , testing is Bleeping Computer
        print(entry.get('title')) # Article Titles
        print(entry.get('link')) # gets link
        
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
        # @TODO: sanitize URL prior to processing
        # @TODO: break this into steps rather than one long ugly line
        print(hashlib.sha256(entry.get('id').encode('utf-8')).hexdigest())
        
        print("\n")

        # @TODO: load all cleaned/sanitized data into a dict to return later
        #sanitized = {
            #"feedTitle": feed.get('title')
        #}

    # @TODO: This is currently returning the original input while testing, change to cleaned/sanitized once it exists
    return feed

def main():
    testURL = "https://www.bleepingcomputer.com/feed/"
    testFeed = FeedGrabber(testURL)


if __name__ == "__main__":
    main()