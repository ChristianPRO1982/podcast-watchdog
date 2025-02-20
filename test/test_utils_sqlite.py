import pytest
import dotenv
import os
from src.logs import Logs
from src.utils_sqlite import PodcastDB


db_path = './podcast_pytest.db'
if os.path.exists(db_path):
    os.remove(db_path)

dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")
logs = Logs()
podcastdb = PodcastDB(logs)


def test_status():
    if DEBUG == '4':
        if not podcastdb.status:
            assert True
    
    else:
        assert False

def test_add_podcast():
    if DEBUG == '4':
        count_before = podcastdb.count_podcasts()
        podcastdb.insert_podcast('category', 'podcast_name', 'rss_feed', 'title', 'link', 'published', 'description')
        count_after = podcastdb.count_podcasts()
        assert count_before + 1 == count_after
    
    else:
        assert False

def test_update_podcast():
    if DEBUG == '4':
        request1 = '''
UPDATE podcasts
   SET category = "category 1",
       podcast_name = "podcast_name 1",
       rss_feed = "rss_feed 1",
       title = "title 1",
       link = "link 1",
       published = "published 1",
       description = "description 1",
       downloaded = 1,
       processed = 1
 WHERE ID = 1
'''
        request2 = '''
UPDATE podcasts_not_exists
   SET category = "category 2"
 WHERE ID = 2
'''
        return1 = podcastdb.update_podcast(request1)
        return2 = podcastdb.update_podcast(request2)
        
        assert return1 == True
        assert return2 == False
    
    else:
        assert False