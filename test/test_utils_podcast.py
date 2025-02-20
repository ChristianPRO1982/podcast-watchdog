import pytest
import dotenv
import os
import shutil
from src.logs import Logs
from src.utils_sqlite import PodcastDB
from src.utils_podcast import Podcasts


if os.path.exists('./downloads/example.mp3'):
    os.remove('./downloads/example.mp3')
if os.path.exists('./downloads/example.txt'):
    os.remove('./downloads/example.txt')
shutil.copy('./test/example.mp3', './downloads')

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


def test_transcribe():
    if DEBUG == '4':
        podcastdb.insert_podcast('category', 'test_transcribe', 'rss_feed', 'title', 'test_transcribe', 'published', 'description')
        request = '''
UPDATE podcasts
   SET downloaded = 1
 WHERE podcast_name = "test_transcribe"
'''
        podcastdb.update_podcast(request)

        count_before = podcastdb.count_podcasts(downloaded=True, transcribed=False)
        podcasts.transcribe_podcasts()
        count_after = podcastdb.count_podcasts(downloaded=True, transcribed=False)
        assert count_before - 1 == count_after
    
    else:
        assert False


def test_summarize():
    if DEBUG == '4':
        podcastdb.insert_podcast('category', 'test_summarize', 'rss_feed', 'title', 'test_summarize', 'published', 'description')
        request = '''
UPDATE podcasts
   SET downloaded = 1,
       transcribed = 1
 WHERE podcast_name = "test_summarize"
'''
        podcastdb.update_podcast(request)

        count_before = podcastdb.count_podcasts(downloaded=True, transcribed=True, summarized=False)
        podcasts.summarize_podcasts()
        count_after = podcastdb.count_podcasts(downloaded=True, transcribed=True, summarized=False)
        assert count_before - 1 == count_after
    
    else:
        assert False