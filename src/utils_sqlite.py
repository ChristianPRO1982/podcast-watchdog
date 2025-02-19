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
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                published TEXT NOT NULL,
                description TEXT NOT NULL,
                downloaded INTEGER DEFAULT 0,
                processed INTEGER DEFAULT 0
            )""")

            self.logs.logging_msg(f"{log_prefix} CREATE TABLE podcasts", 'DEBUG')
        
        except Exception as e:
            self.status = f"{log_prefix} Error: {e}"
            self.logs.logging_msg(self.status, 'ERROR')


    def insert_podcast(self, category, podcast_name, rss_feed, title, link, published, description):
        prefix = f'[{self.__class__.__name__} | insert_podcast]'
        
        try:
            request = f'''
INSERT INTO podcasts (category, podcast_name, rss_feed, title, link, published, description)
    VALUES ("{category}", "{podcast_name}", "{rss_feed}", "{title}", "{link}", "{published}", "{description}")
'''
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)

            self.logs.logging_msg(f"{prefix} podcast saved in 'podcast.db'", 'DEBUG')

        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                self.logs.logging_msg(f"{prefix} Podcast already exists", 'DEBUG')
            else:
                self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
    

    def podcasts(self, downloaded: bool = None, processed: bool = None)->list:
        prefix = f'[{self.__class__.__name__} | podcasts]'

        if downloaded is True:  downloaded_txt = '   AND downloaded = 1'
        if downloaded is False: downloaded_txt = '   AND downloaded = 0'
        if downloaded is None:  downloaded_txt = ''
        if processed is True:   processed_txt = '   AND processed = 1'
        if processed is False:  processed_txt = '   AND processed = 0'
        if processed is None:   processed_txt = ''

        try:
            request = f'''
SELECT *
  FROM podcasts
 WHERE 1 = 1
{downloaded_txt}
{processed_txt}
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
                    row[9]
                )
                podcasts.append(podcast)
            
            return podcasts

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return []
        

    def update_podcast(self, request: str):
        prefix = f'[{self.__class__.__name__} | update_podcast]'
        
        try:
            self.logs.logging_msg(f"{prefix} request: {request}", 'SQL')
            self.cursor.execute(request)
            self.conn.commit()
            self.logs.logging_msg(f"{prefix} podcast updated in 'podcast.db'", 'DEBUG')

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')


    def logout(self):
        self.conn.commit()
        self.conn.close()