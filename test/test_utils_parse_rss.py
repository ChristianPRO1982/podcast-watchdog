import pytest
import dotenv
import os
from src.logs import Logs
from src.utils_sqlite import PodcastDB
from src.utils_parse_rss import ParseRSS


dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")
logs = Logs()
podcastdb = PodcastDB(logs)
parserss = ParseRSS(logs, podcastdb)


def test_parse_rss():
    if DEBUG == '4':
        assert parserss.podcasts == []
    
    else:
        assert False