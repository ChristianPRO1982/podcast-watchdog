import feedparser
import sqlite3
import json
from logs import logging_msg



##################################################
##################################################
##################################################

############
### INIT ###
############
def init()->bool:
    log_prefix = '[utils | parse_rss_feed]'
    try:
        # Create a connection to the SQLite database
        conn = sqlite3.connect('podcast.db')

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Create the podcasts table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            podcast_name TEXT NOT NULL,
            rss_feed TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            published TEXT NOT NULL,
            description TEXT NOT NULL,
            downloaded BOOLEAN DEFAULT FALSE,
            processed BOOLEAN DEFAULT FALSE
        )""")

        conn.commit()
        conn.close()

        return True
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False

######################
### PARSE PODCASTS ###
######################
def parse_rss_feed(category: str, name: str, rss_feed: str) -> bool:
    log_prefix = '[utils | parse_rss_feed]'
    try:
        logging_msg(f"{log_prefix} feed_rss_url: {rss_feed}", 'DEBUG')

        feed = feedparser.parse(rss_feed)

        if feed.bozo:
            raise Exception(f"Failed to parse RSS feed: {feed.bozo_exception}")

        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()
        
        for entry in feed.entries:
            title = entry.get('title', 'No title')
            link = entry.get('link', 'No link')
            published = entry.get('published', 'No publish date')
            description = entry.get('description', 'No description')
            logging_msg(f"----------------------------------------------------------------------------------------------------", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Title: {title}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Link: {link}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Published Date: {published}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Description: {description}", 'DEBUG')
            title = title.replace('"', "''")
            link = link.replace('"', "''")
            published = published.replace('"', "''")
            description = description.replace('"', "''")

            request = f'''
INSERT INTO podcasts (category, podcast_name, rss_feed, title, link, published, description)
     VALUES ("{category}", "{name}", "{rss_feed}", "{title}", "{link}", "{published}", "{description}")
'''
            logging_msg(f"{log_prefix} request: {request}", 'SQL')
            try:
                cursor.execute(request)
            except Exception as e:
                if 'UNIQUE constraint' in str(e):
                    logging_msg(f"{log_prefix} Podcast already exists", 'WARNING')
                else:
                    logging_msg(f"{log_prefix} Error: {e}", 'ERROR')

            conn.commit()

        conn.close()
        logging_msg(f"{log_prefix} >> OK <<", 'DEBUG')
        return True
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False
    

########################
### DOWNLOAD PODCAST ###
########################
def download_podcast(podcast_id: int, podcast_link: str) -> bool:
    log_prefix = '[utils | download_podcast]'
    try:
        logging_msg(f"{log_prefix} podcast_id: {podcast_id}", 'DEBUG')
        logging_msg(f"{log_prefix} podcast_link: {podcast_link}", 'DEBUG')

        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM podcasts WHERE ID = {podcast_id}")
        podcast = cursor.fetchone()
        if podcast is None:
            logging_msg(f"{log_prefix} Podcast not found", 'ERROR')
            return False

        title = podcast[4]
        link = podcast[5]
        published = podcast[6]
        description = podcast[7]
        downloaded = podcast[8]
        processed = podcast[9]

        if downloaded:
            logging_msg(f"{log_prefix} Podcast already downloaded", 'WARNING')
            return False

        logging_msg(f"----------------------------------------------------------------------------------------------------", 'DEBUG')
        logging_msg(f"{log_prefix} Podcast Title: {title}", 'DEBUG')
        logging_msg(f"{log_prefix} Podcast Link: {link}", 'DEBUG')
        logging_msg(f"{log_prefix} Podcast Published Date: {published}", 'DEBUG')
        logging_msg(f"{log_prefix} Podcast Description: {description}", 'DEBUG')

        return True
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False


##################################################
##################################################
##################################################

### PARSE JSON ###
def parse_json(json_file: str) -> list:
    log_prefix = '[utils | parse_json]'
    try:
        logging_msg(f"{log_prefix} json_file: {json_file}", 'DEBUG')

        with open(json_file, 'r', encoding='utf-8') as file:
            feeds = json.load(file)
        return feeds
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return []