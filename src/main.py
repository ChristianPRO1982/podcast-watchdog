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
if utils.init():
    FEED_RSS = os.getenv("FEED_RSS")
    utils.parse_rss_feed(FEED_RSS)
logging_msg("END PROGRAM", "WARNING")
