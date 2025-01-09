import dotenv
import os
from logs import init_log, logging_msg
import utils



##################################################
##################################################
##################################################

############
### MAIN ###
############
dotenv.load_dotenv(override=True)
init_log()
logging_msg("START PROGRAM", "WARNING")

podcast_list = utils.parse_json(os.getenv("RSS_FEEDS"))

if utils.init():
    for podcast in podcast_list:
        category = podcast["category"]
        name = podcast["name"]
        rss_feed = podcast["rss_feed"]
        utils.parse_rss_feed(rss_feed)

logging_msg("END PROGRAM", "WARNING")
