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