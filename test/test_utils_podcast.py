import pytest
import dotenv
import os
from src.logs import Logs
from src.utils_sqlite import PodcastDB
from src.utils_podcast import Podcasts


dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")
logs = Logs()
podcastdb = PodcastDB(logs)
podcasts = Podcasts(logs, podcastdb)


def test_podcasts():
    if DEBUG == '4':
        podcastdb.insert_podcast('category', 'test_podcasts', 'rss_feed', 'title', 'test_podcasts', 'published', 'description')
        count_before = podcastdb.count_podcasts(downloaded=False)
        podcasts.download_podcasts()
        count_after = podcastdb.count_podcasts(downloaded=False)
        assert count_before - 1 == count_after
    
    else:
        assert False