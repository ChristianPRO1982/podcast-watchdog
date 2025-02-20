import requests
from bs4 import BeautifulSoup
import os


######################################################################################################################################################
class Podcasts():
    def __init__(self, logs, podcastdb):
        self.logs = logs
        self.podcastdb = podcastdb

        self.FOLDER_PATH = os.getenv("FOLDER_PATH")
        self.PREFIX = os.getenv("PREFIX")

        self.podcasts = []
    

    def download_podcasts(self)->bool:
        prefix = f'[{self.__class__.__name__} | download_podcasts]'

        try:
            self.podcasts.clear()
            self.podcasts = self.podcastdb.podcasts(downloaded=False)

            for podcast in self.podcasts:
                podcast.download_podcast()
                podcast.update_podcast()
            
            return True

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return False


    def transcribe_podcasts(self):
        prefix = f'[{self.__class__.__name__} | transcribe_podcasts]'

        try:
            self.podcasts.clear()
            self.podcasts = self.podcastdb.podcasts(downloaded=True, processed=False)

            for podcast in self.podcasts:
                podcast_file_name = os.path.abspath(f'./{self.FOLDER_PATH}/{self.PREFIX}{podcast.id}.mp3')
                text_file_name    = os.path.abspath(f'./{self.FOLDER_PATH}/{self.PREFIX}{podcast.id}.txt')
                self.logs.logging_msg(f"{prefix} podcast_file_name: {podcast_file_name}", 'DEBUG')
                self.logs.logging_msg(f"{prefix} text_file_name: {text_file_name}", 'DEBUG')

                ###############
                ### WHISPER ###
                ###############
                try:
                    response = requests.post('http://127.0.0.1:9000/transcribe/', params={'file_path': podcast_file_name})
                    response_data = response.json()

                    if response.status_code == 200:
                        podcast.processed = 1
                        self.logs.logging_msg(f"{prefix} [API status:{response.status_code}] Transcription successful for podcast: [{podcast.id}] {podcast.title}", 'DEBUG')
                    else:
                        podcast.processed = 2
                        self.logs.logging_msg(f"{prefix} [API status:{response.status_code}] Transcription failed for podcast: [{podcast.id}] {podcast.title} with error: {response_data.get('error', 'Unknown error')}", 'ERROR')
                
                except Exception as e:
                    podcast.processed = 3
                    self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')

                ############################
                ### REPLACE .MP3 BY .TXT ###
                ############################
                if podcast.processed == 1:
                    try:
                        with open(text_file_name, 'w', encoding='utf-8') as text_file:
                            text_file.write(response_data.get('transcription_text', ''))
                        self.logs.logging_msg(f"{prefix} Transcription saved: {text_file_name}", 'DEBUG')

                        os.remove(podcast_file_name)
                        self.logs.logging_msg(f"{prefix} Podcast file removed: {podcast_file_name}", 'DEBUG')

                    except Exception as e:
                        podcast.processed = 4
                        self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
                        
                podcast.update_podcast()

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')


######################################################################################################################################################
class Podcast():
    def __init__(self, logs, podcastdb, id, category, name, rss_feed, title, link, published, description, downloaded, processed):
        self.logs = logs
        self.podcastdb = podcastdb

        self.id = id
        self.category = category
        self.name = name
        self.rss_feed = rss_feed
        self.title = title
        self.link = link
        self.published = published
        self.description = description
        self.downloaded = downloaded
        self.processed = processed

        self.FOLDER_PATH = os.getenv("FOLDER_PATH")
        self.PREFIX = os.getenv("PREFIX")

        os.makedirs(f'./{self.FOLDER_PATH}/', exist_ok=True)
    

    def update_podcast(self):
        prefix = f'[{self.__class__.__name__} | update_podcast]'

        try:
            request = f'''
UPDATE podcasts
   SET category = "{self.category}",
       podcast_name = "{self.name}",
       rss_feed = "{self.rss_feed}",
       title = "{self.title}",
       link = "{self.link}",
       published = "{self.published}",
       description = "{self.description}",
       downloaded = {self.downloaded},
       processed = {self.processed}
 WHERE id = {self.id}
'''
            self.podcastdb.update_podcast(request)
            self.logs.logging_msg(f"{prefix} podcast updated: [{self.id}] {self.title}", 'DEBUG')

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
    

    def download_podcast(self):
        prefix = f'[{self.__class__.__name__} | download_podcast]'

        try:
            self.logs.logging_msg(f"{prefix} downloading podcast: [{self.id}] {self.title}", 'DEBUG')

            try:
                response = requests.get(self.link)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if self.link.startswith('https://shows.acast.com'):
                    self.logs.logging_msg(f"{prefix} self.link.startswith('https://shows.acast.com')", 'DEBUG')
                    mp3_links = [
                        a['content'] for a in soup.find_all('meta', content=True)
                        if a['content'].endswith('.mp3')
                    ]
                elif self.link.startswith('https://feed.ausha.co') or self.link.startswith('https://podcast.ausha.co'):
                    self.logs.logging_msg(f"{prefix} self.link.startswith('https://feed.ausha.co')", 'DEBUG')
                    mp3_links = [
                        a['href'] for a in soup.find_all('a', href=True)
                        if a['href'].endswith('.mp3')
                    ]
                elif self.link.startswith('https://sphinx.acast.com/'):
                    self.logs.logging_msg(f"{prefix} self.link.startswith('https://sphinx.acast.com/')", 'DEBUG')
                    mp3_links = [self.link]
                elif self.link.startswith('https://anchor.fm/'):
                    self.logs.logging_msg(f"{prefix} self.link.startswith('https://anchor.fm/')", 'DEBUG')
                    mp3_links = [self.link]
                else:
                    self.logs.logging_msg(f"{prefix} self.link.startswith: else", 'DEBUG')
                    self.logs.logging_msg(f"{prefix} can't to parse the self.link: {self.link}", 'WARNING')
                    mp3_links = []
                
                self.logs.logging_msg("a", mp3_links)
                self.link = mp3_links[0]
            
            except Exception as e:
                if '404' in str(e):
                    self.logs.logging_msg(f"{prefix} Podcast link not found: {self.link}", 'WARNING')
                    self.downloaded = 404
                else:
                    self.logs.logging_msg(f"{prefix} Error parsing podcast link: {e}", 'ERROR')
                    self.downloaded = 3

            
            if self.downloaded == 0:
                try:
                    file_name = os.path.join(self.FOLDER_PATH, f'{self.PREFIX}{self.id}.mp3')
                    response = requests.get(self.link)
                    response.raise_for_status()
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    self.logs.logging_msg(f"{prefix} Podcast downloaded: {file_name}", 'DEBUG')
                    self.downloaded = 1

                except Exception as e:
                    self.logs.logging_msg(f"{prefix} Error downloading podcast: {e}", 'ERROR')
                    self.downloaded = 2

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')