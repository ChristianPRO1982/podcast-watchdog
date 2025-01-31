import feedparser
import requests
import whisper
import openai
from bs4 import BeautifulSoup
import sqlite3
import json
import os
from logs import logging_msg



####################################################################################################
####################################################################################################
####################################################################################################

############
### INIT ###
############
def init()->bool:
    log_prefix = '[utils | parse_rss_feed]'
    try:
        FOLDER_PATH = os.getenv("FOLDER_PATH")
        os.makedirs(f'./{FOLDER_PATH}/', exist_ok=True)

        conn = sqlite3.connect('podcast.db')

        cursor = conn.cursor()

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
            downloaded INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0
        )""")

        conn.commit()
        conn.close()

        return True
    
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False


####################################################################################################
####################################################################################################
####################################################################################################

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
            if 'feeds.acast.com' in rss_feed:
                links = entry.get('links', [])
                # link = links[1]['href'] if len(links) > 1 else 'No link'
                link = next((l['href'] for l in links if l['href'].startswith('https://sphinx.acast.com')), 'No link')
                logging_msg(f"{log_prefix} 'feeds.acast.com' Podcast Link: {link}", 'DEBUG')
            elif 'feed.ausha.co' in rss_feed:
                link = entry.get('link', 'No link')
                logging_msg(f"{log_prefix} 'feed.ausha.co' Podcast Link: {link}", 'DEBUG')
            else:
                link = entry.get('', 'No link')
                logging_msg(f"{log_prefix} OTHER Podcast Link: {link}", 'WARNING')
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
                    logging_msg(f"{log_prefix} Podcast already exists", 'DEBUG')
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
def download_podcast(FOLDER_PATH, PREFIX) -> bool:
    log_prefix = '[utils | download_podcast]'
    try:
        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()

        request = f'''
SELECT id, podcast_name, link
  FROM podcasts
 WHERE downloaded = 0
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            id = row[0]
            podcast_name = row[1]
            link = row[2]
            downloaded = 0
            logging_msg(f"{log_prefix} id: {row[0]} / podcast_name: {podcast_name}")

            try:
                response = requests.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if link.startswith('https://shows.acast.com'):
                    mp3_links = [
                        a['content'] for a in soup.find_all('meta', content=True)
                        if a['content'].endswith('.mp3')
                    ]
                elif link.startswith('https://feed.ausha.co'):
                    mp3_links = [
                        a['href'] for a in soup.find_all('a', href=True)
                        if a['href'].endswith('.mp3')
                    ]
                elif link.startswith('https://sphinx.acast.com/p/open/s'):
                    mp3_links = [link]
                else:
                    logging_msg(f"{log_prefix} link: {link}", 'WARNING')
                    mp3_links = []

                link = mp3_links[0]
            
            except Exception as e:
                if '404' in str(e):
                    logging_msg(f"{log_prefix} Podcast link not found: {link}", 'WARNING')
                    downloaded = 404
                else:
                    logging_msg(f"{log_prefix} Error parsing podcast link: {e}", 'ERROR')
                    downloaded = 3

            
            if downloaded == 0:
                try:
                    file_name = os.path.join(FOLDER_PATH, f'{PREFIX}{id}.mp3')
                    response = requests.get(link)
                    response.raise_for_status()
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    logging_msg(f"{log_prefix} Podcast downloaded: {file_name}", 'DEBUG')
                    downloaded = 1

                except Exception as e:
                    logging_msg(f"{log_prefix} Error downloading podcast: {e}", 'ERROR')
                    downloaded = 2

            request = f'''
UPDATE podcasts
   SET downloaded = {downloaded}
 WHERE id = {id}
'''
            cursor.execute(request)
            conn.commit()
            logging_msg(f"{log_prefix} Podcast updated: {id}", 'DEBUG')
        
        conn.close()

        return True
    
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False
    

####################################################################################################
####################################################################################################
####################################################################################################

##################
### TRANSCRIBE ###
##################
def transcribe_all_podcasts() -> bool:
    log_prefix = '[utils | transcribe_all_podcasts]'
    try:
        FOLDER_PATH = os.getenv("FOLDER_PATH")
        PREFIX = os.getenv("PREFIX")
        
        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()

        request = f'''
SELECT id, podcast_name
  FROM podcasts
 WHERE downloaded = 1
   AND processed = 0
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            logging_msg(f"{log_prefix} id: {row[0]} / podcast_name: {row[1]}")
            podcast_file_name = os.path.join(FOLDER_PATH, f'{PREFIX}{row[0]}.mp3')
            text_file_name = os.path.join(FOLDER_PATH, f'{PREFIX}{row[0]}.txt')

            if os.path.exists(podcast_file_name):
                logging_msg(f"{log_prefix} File exists: {podcast_file_name}", 'DEBUG')
                
                transcribe_text = transcribe_podcast(podcast_file_name)
                
                if transcribe_text:
                    with open(text_file_name, 'w', encoding='utf-8') as text_file:
                        text_file.write(transcribe_text)
                    logging_msg(f"{log_prefix} Transcription saved: {text_file_name}", 'DEBUG')
                    processed = 1
                else:
                    processed = 2

                os.remove(podcast_file_name)
                logging_msg(f"{log_prefix} Podcast file removed: {podcast_file_name}", 'DEBUG')

                request = f'''
UPDATE podcasts
   SET processed = {processed}
 WHERE id = {row[0]}
'''
                logging_msg(f"{log_prefix} request: {request}", 'SQL')
                cursor.execute(request)
                conn.commit()
                logging_msg(f"{log_prefix} Podcast updated: {row[0]}", 'DEBUG')

            else:
                logging_msg(f"{log_prefix} File does not exist: {podcast_file_name}", 'WARNING')
        
        conn.close()

        return True
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        conn.close()
        return False


###############
### WHISPER ###
###############
def transcribe_podcast(file_name: str) -> str:
    log_prefix = '[utils | transcribe_podcast]'
    try:
        model = whisper.load_model("base")  # "base" / "tiny" / "small" / "medium" / "large"
        result = model.transcribe(str(file_name))

        transcription = result.get("text", "")
        if not transcription:
            logging_msg(f"{log_prefix} Error: {e}", 'WARNING')
            return None

        return transcription
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return None


####################################################################################################
####################################################################################################
####################################################################################################

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