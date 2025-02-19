import dotenv
import os
from logs import init_log, logging_msg
import utils_parse_rss


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    if init_log():
        logging_msg("START PROGRAM", "WARNING")

        logging_msg("utils.parse_json START", 'WARNING')
        RSS_FEEDS = utils_parse_rss.parse_json(os.getenv("RSS_FEEDS"))
        FOLDER_PATH = os.getenv("FOLDER_PATH")
        PREFIX = os.getenv("PREFIX")

        if utils_parse_rss.init():
            for podcast in RSS_FEEDS:
                category = podcast["category"]
                name = podcast["name"]
                rss_feed = podcast["rss_feed"]
                logging_msg(f"utils.parse_rss_feed {name} START")
                stop_and_go = utils_parse_rss.parse_rss_feed(category, name, rss_feed)
                if stop_and_go:
                    logging_msg("utils.download_podcast START", 'WARNING')
                    utils_parse_rss.download_podcast(FOLDER_PATH, PREFIX)
            
            logging_msg("utils.transcribe_all_podcasts START", 'WARNING')
            stop_and_go = utils_parse_rss.transcribe_all_podcasts()
            if stop_and_go:
                logging_msg("utils.summarize START", 'WARNING')
                # utils.summarize()

        logging_msg("END PROGRAM", "WARNING")