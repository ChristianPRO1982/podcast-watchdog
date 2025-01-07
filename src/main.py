from logs import init_log, logging_msg
import dotenv



### DOWNLOAD PODCASTS ###
def parse_rss_feed():
    pass


############
### MAIN ###
############
dotenv.load_dotenv(override=True)
init_log()
logging_msg("START PROGRAM", "WARNING")
parse_rss_feed()
logging_msg("END PROGRAM", "WARNING")
