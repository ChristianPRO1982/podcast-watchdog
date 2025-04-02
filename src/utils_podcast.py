import openai
import requests
from bs4 import BeautifulSoup
import os
import re
import json
from datetime import datetime, timedelta



class Podcasts():
    def __init__(self, logs, podcastdb):
        self.logs = logs
        self.podcastdb = podcastdb

        self.DEBUG = os.getenv("DEBUG")
        self.FOLDER_PATH = os.getenv("FOLDER_PATH")
        self.PREFIX = os.getenv("PREFIX")
        self.OPENAI_PROMPTS = os.getenv("OPENAI_PROMPTS")
        if self.DEBUG == '0':
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        else:
            self.OPENAI_API_KEY = ""

        try:
            with open(self.OPENAI_PROMPTS, 'r', encoding='utf-8') as file:
                self.openai_prompts = json.load(file)
                self.logs.logging_msg(f"OpenAI prompts loaded", 'DEBUG')

        except Exception as e:
            self.logs.logging_msg(f"Error loading OpenAI prompts: {e}", 'ERROR')
            self.openai_prompts = {}

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
            self.podcasts = self.podcastdb.podcasts(downloaded=True, transcribed=False)

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
                        podcast.transcribed = 1
                        self.logs.logging_msg(f"{prefix} [API status:{response.status_code}] Transcription successful for podcast: [{podcast.id}] {podcast.title}", 'INFO')
                    else:
                        podcast.transcribed = 2
                        self.logs.logging_msg(f"{prefix} [API status:{response.status_code}] Transcription failed for podcast: [{podcast.id}] {podcast.title} with error: {response_data.get('error', 'Unknown error')}", 'ERROR')
                
                except Exception as e:
                    podcast.transcribed = 3
                    self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')

                ############################
                ### REPLACE .MP3 BY .TXT ###
                ############################
                if podcast.transcribed == 1:
                    try:
                        with open(text_file_name, 'w', encoding='utf-8') as text_file:
                            text_file.write(response_data.get('transcription_text', ''))
                        self.logs.logging_msg(f"{prefix} Transcription saved: {text_file_name}", 'DEBUG')

                        os.remove(podcast_file_name)
                        self.logs.logging_msg(f"{prefix} Podcast file removed: {podcast_file_name}", 'DEBUG')

                    except Exception as e:
                        podcast.transcribed = 4
                        self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
                        
                podcast.update_podcast()

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')


    def summarize_podcasts(self)->bool:
        prefix = f'[{self.__class__.__name__} | summarize_podcasts]'

        try:
            if self.DEBUG != '0':
                raise Exception("DEBUG mode is enabled > use OpenAI API is disabled")
            
            openai.api_key = self.OPENAI_API_KEY

            published_int_min = (datetime.now() - timedelta(days=int(os.getenv('SUMMARY_DAYS_LIMIT')))).strftime('%Y%m%d')
            self.podcasts.clear()
            self.podcasts = self.podcastdb.podcasts(downloaded=True, transcribed=True, summarized=False, published_int_min=published_int_min, summarize=True)

            for podcast in self.podcasts:
                try:
                    text_file_name    = os.path.abspath(f'./{self.FOLDER_PATH}/{self.PREFIX}{podcast.id}.txt')
                    
                    podcasts_prompt = self.openai_prompts['podcasts']
                    for podcast_prompt in podcasts_prompt:
                        if podcast_prompt['category'] == podcast.category:
                            role = podcast_prompt['role']
                            pre_prompt = podcast_prompt['pre_prompt']
                            break
                    
                    prompt = pre_prompt + "\n\nTranscription:\n" + open(text_file_name, 'r', encoding='utf-8').read()

                    ##################
                    ### OPENAI API ###
                    ##################
                    response = openai.ChatCompletion.create(
                        # model="gpt-4",
                        model="chatgpt-4o-latest",
                        messages=[
                            {"role": "system", "content": role},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    podcast.summarized = 1
                    podcast.summary = response['choices'][0]['message']['content']
                    with open(f'./{self.FOLDER_PATH}/{self.PREFIX}{podcast.id}_summary.txt', 'w', encoding='utf-8') as summary_file:
                        summary_file.write(podcast.summary)
                    self.logs.logging_msg(f"{prefix} Summarization successful for podcast: [{podcast.id}] {podcast.title}", 'INFO')

                except Exception as e:
                    podcast.summarized = 2
                    self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
                
                podcast.update_podcast()

            return True

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return False
        

    def update_published_int(self):
        prefix = f'[{self.__class__.__name__} | update_published_int]'

        try:
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')

            self.podcasts.clear()
            self.podcasts = self.podcastdb.podcasts()

            for podcast in self.podcasts:
                podcast.update_podcast_published_int()
            
            return True

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return False


######################################################################################################################################################


class Podcast():
    def __init__(self, logs, podcastdb, id, category, name, rss_feed, summarize, title, link, published, description, downloaded, transcribed, summarized, summary=None):
        self.logs = logs
        self.podcastdb = podcastdb

        self.id = id
        self.category = category
        self.name = name
        self.rss_feed = rss_feed
        self.summarize = summarize
        self.title = title
        self.link = link
        self.published = published
        self.description = description
        self.downloaded = downloaded
        self.transcribed = transcribed
        self.summarized = summarized
        self.summary = summary

        self.FOLDER_PATH = os.getenv("FOLDER_PATH")
        self.PREFIX = os.getenv("PREFIX")

        os.makedirs(f'./{self.FOLDER_PATH}/', exist_ok=True)
    

    def update_podcast(self):
        prefix = f'[{self.__class__.__name__} | update_podcast]'

        try:
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')

            request = f'''
UPDATE podcasts
   SET category = "{self.category}",
       podcast_name = "{self.name}",
       rss_feed = "{self.rss_feed}",
       summarize = {self.summarize},
       title = "{self.title}",
       published = "{self.published}",
       description = "{self.description}",
       downloaded = {self.downloaded},
       transcribed = {self.transcribed},
       summarized = {self.summarized},
       summary = "{self.magic_quotes(self.summary)}"
 WHERE id = {self.id}
'''
            self.podcastdb.update_podcast(request)
            self.logs.logging_msg(f"{prefix} [{self.id}] podcast updated: [{self.id}] {self.title}", 'DEBUG')

        except Exception as e:
            self.logs.logging_msg(f"{prefix} [{self.id}] Error: {e}", 'WARNING')


    def magic_quotes(self, text):
        prefix = f'[{self.__class__.__name__} | magic_quotes]'
        try:
            return text.replace('"', '”')
        except Exception as e:
            self.logs.logging_msg(f"{prefix} [{self.id}] Error: {e}", 'WARNING')
            return text


    def update_podcast_published_int(self):
        prefix = f'[{self.__class__.__name__} | update_podcast_published_int]'

        try:
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')

            date_format = "%a, %d %b %Y %H:%M:%S %Z" if "GMT" in self.published else "%a, %d %b %Y %H:%M:%S %z"
            published_date = datetime.strptime(self.published, date_format)
            published_int = int(published_date.strftime("%Y%m%d"))

            request = f'''
UPDATE podcasts
   SET published_int = {published_int}
 WHERE id = {self.id}
'''
            self.podcastdb.update_podcast(request)
            self.logs.logging_msg(f"{prefix} [{self.id}] podcast updated: [{self.id}] {self.published} > {published_int}", 'DEBUG')

        except Exception as e:
            self.logs.logging_msg(f"{prefix} [{self.id}] Error: {e}", 'WARNING')
    

    def download_podcast(self):
        prefix = f'[{self.__class__.__name__} | download_podcast]'

        try:
            self.logs.logging_msg(f"{prefix} [{self.id}] downloading podcast: [{self.id}] {self.title}", 'DEBUG')

            try:
                response = requests.get(self.link)
                response.raise_for_status()
                
                try:
                    soup = BeautifulSoup(response.content, 'html.parser')
                
                    if self.link.startswith('https://shows.acast.com'):
                        self.logs.logging_msg(f"{prefix} self.link.startswith('https://shows.acast.com')", 'DEBUG')
                        mp3_links = [
                            a['content'] for a in soup.find_all('meta', content=True)
                            if a['content'].endswith('.mp3')
                        ]
                    elif self.link.startswith('https://feed.ausha.co') or self.link.startswith('https://podcast.ausha.co'):
                        self.logs.logging_msg(f"{prefix} self.link.startswith('https://feed.ausha.co')", 'DEBUG')
                        html_content = soup.prettify()
                        mp3_links = [
                            a['href'] for a in soup.find_all('a', href=True)
                            if a['href'].endswith('.mp3')
                        ]
                        if len(mp3_links) == 0:
                            mp3_links = re.findall(r'"(https://dts\.podtrac\.com/redirect\.mp3/audio\.ausha\.co/.*?\.mp3)"', html_content)
                        # mp3_links = [
                        #   # a['href'] for a in soup.find_all('a', href=True)
                            # if a['href'].startswith('https://dts.podtrac.com/redirect.mp3/audio.ausha.co/') and a['href'].endswith('.mp3')
                            # if a['href'].endswith('.mp3')
                        # ]
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
                
                except Exception as e:
                    self.logs.logging_msg(f"{prefix} [{self.id}] Error parsing podcast link: {e}", 'DEBUG')
                    mp3_links = [self.link]
                finally:
                    self.logs.logging_msg(f"{prefix} [{self.id}] mp3_links: {mp3_links}", 'DEBUG')
                
                self.logs.logging_msg("a", mp3_links)
                self.link = mp3_links[0]
            
            except Exception as e:
                if '404' in str(e):
                    self.logs.logging_msg(f"{prefix} [{self.id}] Podcast link not found: {self.link}", 'WARNING')
                    self.downloaded = 404
                else:
                    self.logs.logging_msg(f"{prefix} [{self.id}] Error to find podcast link: {e}", 'ERROR')
                    self.downloaded = 3

            
            if self.downloaded == 0:
                try:
                    file_name = os.path.join(self.FOLDER_PATH, f'{self.PREFIX}{self.id}.mp3')
                    response = requests.get(self.link)
                    response.raise_for_status()
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    self.logs.logging_msg(f"{prefix} [{self.id}] Podcast downloaded: {file_name}", 'DEBUG')
                    self.downloaded = 1

                except Exception as e:
                    self.logs.logging_msg(f"{prefix} [{self.id}] Error downloading podcast: {e}", 'ERROR')
                    self.downloaded = 2

        except Exception as e:
            self.logs.logging_msg(f"{prefix} [{self.id}] Error: {e}", 'WARNING')