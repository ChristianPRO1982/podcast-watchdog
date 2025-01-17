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

logging_msg("utils.parse_json START", 'WARNING')
podcast_list = utils.parse_json(os.getenv("RSS_FEEDS"))

if utils.init():
    for podcast in podcast_list:
        category = podcast["category"]
        name = podcast["name"]
        rss_feed = podcast["rss_feed"]
        logging_msg(f"utils.parse_rss_feed {name} START", 'WARNING')
        stop_and_go = utils.parse_rss_feed(category, name, rss_feed)
        if stop_and_go:
            logging_msg("utils.download_podcast START", 'WARNING')
            utils.download_podcast()
    
    logging_msg("utils.transcribe_all_podcasts START", 'WARNING')
    stop_and_go = utils.transcribe_all_podcasts()
    if stop_and_go:
        logging_msg("utils.summarize START", 'WARNING')
        # utils.summarize()

logging_msg("END PROGRAM", "WARNING")
