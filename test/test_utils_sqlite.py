import pytest
import dotenv
import os
from src.logs import Logs
from src.utils_sqlite import PodcastDB


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