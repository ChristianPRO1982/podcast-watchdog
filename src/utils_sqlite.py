import sqlite3
import os
from src.utils_podcast import Podcast


class PodcastDB:
    def __init__(self, logs):
        self.status = None # status == None > all right, status != None > error
        self.logs = logs

        self.DEBUG = os.getenv("DEBUG")

        if self.DEBUG == '4': # debug mode for pytest
            self.conn = sqlite3.connect('podcast_pytest.db')
        else:
            self.conn = sqlite3.connect('podcast.db')
        self.cursor = self.conn.cursor()
        self.init()


    def init(self):
        log_prefix = f'[{self.__class__.__name__} | init]'
        
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS podcasts (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                podcast_name TEXT NOT NULL,
                rss_feed TEXT NOT NULL,
                summarize INTEGER DEFAULT 0,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                published TEXT NOT NULL,
                published_int INTEGER,
                description TEXT NOT NULL,
                downloaded INTEGER DEFAULT 0,
                transcribed INTEGER DEFAULT 0,
                summarized INTEGER DEFAULT 0,
                summary TEXT DEFAULT NULL
            )""")

            self.logs.logging_msg(f"{log_prefix} CREATE TABLE `podcasts`", 'DEBUG')
        
        except Exception as e:
            self.status = f"{log_prefix} Error: {e}"
            self.logs.logging_msg(self.status, 'ERROR')


    def insert_podcast(self, category, podcast_name, rss_feed, summarize, title, link, published, description):
        prefix = f'[{self.__class__.__name__} | insert_podcast]'
        
        try:
            request = f'''
INSERT INTO podcasts (category, podcast_name, rss_feed, summarize, title, link, published, description)
     VALUES ("{category}", "{podcast_name}", "{rss_feed}", "{summarize}", "{title}", "{link}", "{published}", "{description}")
'''
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)
            self.conn.commit()

            self.logs.logging_msg(f"{prefix} podcast saved in 'podcast.db'", 'DEBUG')

        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                self.logs.logging_msg(f"{prefix} Podcast already exists", 'DEBUG')
            else:
                self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
    

    def podcasts(self, downloaded: bool = None, transcribed: bool = None, summarized: bool = None, published_int_min: int = None)->list:
        prefix = f'[{self.__class__.__name__} | podcasts]'

        if downloaded is True:  downloaded_txt = '   AND downloaded = 1'
        if downloaded is False: downloaded_txt = '   AND downloaded = 0'
        if downloaded is None:  downloaded_txt = ''
        if transcribed is True:   transcribed_txt = '   AND transcribed = 1'
        if transcribed is False:  transcribed_txt = '   AND transcribed = 0'
        if transcribed is None:   transcribed_txt = ''
        if summarized is True:   summarized_txt = '   AND summarized = 1'
        if summarized is False:  summarized_txt = '   AND summarized = 0'
        if summarized is None:   summarized_txt = ''
        if published_int_min is not None: published_int_min_txt = '   AND published_int >= ' + str(published_int_min)
        if published_int_min is None:     published_int_min_txt = ''

        try:
            request = f'''
SELECT *
  FROM podcasts
 WHERE 1 = 1
{downloaded_txt}
{transcribed_txt}
{summarized_txt}
{published_int_min_txt}
'''
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)

            podcasts = []
            for row in self.cursor.fetchall():
                podcast = Podcast(
                    self.logs,
                    self,
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    row[11],
                    row[12]
                )
                podcasts.append(podcast)
            
            return podcasts

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return []


    def count_podcasts(self, downloaded: bool = None, transcribed: bool = None, summarized: bool = None)->int:
        prefix = f'[{self.__class__.__name__} | count_podcasts]'

        if downloaded is True:  downloaded_txt = '   AND downloaded = 1'
        if downloaded is False: downloaded_txt = '   AND downloaded = 0'
        if downloaded is None:  downloaded_txt = ''
        if transcribed is True:   transcribed_txt = '   AND transcribed = 1'
        if transcribed is False:  transcribed_txt = '   AND transcribed = 0'
        if transcribed is None:   transcribed_txt = ''
        if summarized is True:   summarized_txt = '   AND summarized = 1'
        if summarized is False:  summarized_txt = '   AND summarized = 0'
        if summarized is None:   summarized_txt = ''
        
        try:
            request = f'''
SELECT COUNT(1)
  FROM podcasts
 WHERE 1 = 1
{downloaded_txt}
{transcribed_txt}
{summarized_txt}
'''
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)
            count = self.cursor.fetchone()[0]
            self.logs.logging_msg(f"{prefix} count: {count}", 'DEBUG')
            return count

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return 0
        

    def update_podcast(self, request: str)->bool:
        prefix = f'[{self.__class__.__name__} | update_podcast]'
        
        try:
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)
            self.conn.commit()
            self.logs.logging_msg(f"{prefix} podcast updated in 'podcast.db'", 'DEBUG')

            return True

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return False


    def logout(self):
        self.conn.commit()
        self.conn.close()