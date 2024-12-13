import os
import dotenv
import json
from src.logs import init_log, logging_msg



dotenv.load_dotenv('.env', override=True)
DEBUG = os.getenv("DEBUG")
RSS_FEEDS = os.getenv("RSS_FEEDS")


### DOWNLOAD PODCASTS ###
def parse_rss_feed():
    print(os.path.abspath(RSS_FEEDS))
    rss_feeds = json.loads(os.path.abspath(RSS_FEEDS))
    # for feed in rss_feeds:
    #     print(f"Category: {feed['category']}, Name: {feed['name']}, RSS Feed: {feed['rss_feed']}")


############
### MAIN ###
############
init_log()
logging_msg("START PROGRAM", "WARNING")
parse_rss_feed()
logging_msg("END PROGRAM", "WARNING")
