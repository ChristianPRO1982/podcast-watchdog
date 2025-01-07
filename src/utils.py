from logs import logging_msg
import feedparser



##################################################
##################################################
##################################################

### DOWNLOAD PODCASTS ###
def parse_rss_feed(feed_rss_url: str) -> bool:
    log_prefix = '[ext-all_files | init]'
    try:
        logging_msg(f"{log_prefix} feed_rss_url: {feed_rss_url}", 'DEBUG')

        # Parse the RSS feed
        feed = feedparser.parse(feed_rss_url)

        # Check for feed parsing errors
        if feed.bozo:
            raise Exception(f"Failed to parse RSS feed: {feed.bozo_exception}")

        # List all available podcasts and their information
        for entry in feed.entries:
            title = entry.get('title', 'No title')
            link = entry.get('link', 'No link')
            published = entry.get('published', 'No publish date')
            description = entry.get('description', 'No description')

            logging_msg(f"{log_prefix} Podcast Title: {title}", 'INFO')
            logging_msg(f"{log_prefix} Podcast Link: {link}", 'INFO')
            logging_msg(f"{log_prefix} Podcast Published Date: {published}", 'INFO')
            logging_msg(f"{log_prefix} Podcast Description: {description}", 'INFO')

        logging_msg(f"{log_prefix} OK")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False