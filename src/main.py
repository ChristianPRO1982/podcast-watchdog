import dotenv
from logs import Logs
from utils_sqlite import PodcastDB
from utils_parse_rss import ParseRSS


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logs = Logs()
    podcastdb = PodcastDB(logs)

    if not logs.status and not podcastdb.status:
        logs.logging_msg("START PROGRAM", "WARNING")

        parser = ParseRSS(logs, podcastdb)
        print(parser.feeds)

        podcastdb.logout()

        logs.logging_msg("END PROGRAM", "WARNING")

    else:
        print("logger.status:", logs.status)
        print("podcastdb.status:", podcastdb.status)
        exit(1)