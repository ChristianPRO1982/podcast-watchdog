import sqlite3


class PodcastDB:
    def __init__(self, logs):
        self.status = None # status == None > all right, status != None > error
        self.logs = logs
        self.conn = sqlite3.connect('podcast.db')
        self.cursor = self.conn.cursor()
        self.init()
    

    def __str__(self):
        return self.__class__.__name__


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
        log_prefix = f'[{self.__class__.__name__} | insert_podcast]'


    def logout(self):
        self.conn.commit()
        self.conn.close()