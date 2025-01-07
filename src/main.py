import dotenv
import os
from logs import init_log, logging_msg
from utils import parse_rss_feed



##################################################
##################################################
##################################################

############
### MAIN ###
############
dotenv.load_dotenv(override=True)
init_log()
logging_msg("START PROGRAM", "WARNING")
FEED_RSS = os.getenv("FEED_RSS")
parse_rss_feed(FEED_RSS)
logging_msg("END PROGRAM", "WARNING")
