import feedparser
import random
import database

def get_latest_news():
    feeds = database.get_feeds()
    if not feeds:
        return None
    
    # Randomly select a feed
    feed_url, region = random.choice(feeds)
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        return None
    
    # Get latest 5 entries and choose randomly
    entry = random.choice(feed.entries[:5])
    
    # Extract image if available
    image_url = None
    if 'media_content' in entry:
        for media in entry.media_content:
            if media.get('type', '').startswith('image/'):
                image_url = media['url']
                break
    
    return {
        'title': entry.title,
        'summary': entry.description if hasattr(entry, 'description') else "",
        'link': entry.link,
        'image': image_url,
        'region': region
    }