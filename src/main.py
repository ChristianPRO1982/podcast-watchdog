import dotenv
from logs import Logs
from utils_sqlite import PodcastDB
from utils_parse_rss import ParseRSS
from utils_podcast import Podcasts


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logs = Logs()
    podcastdb = PodcastDB(logs)

    if not logs.status and not podcastdb.status:
        logs.logging_msg("START PROGRAM", "WARNING")

        logs.logging_msg("parsing RSS feeds")
        ParseRSS(logs, podcastdb)

        logs.logging_msg("download podcasts")
        podcasts = Podcasts(logs, podcastdb)
        podcasts.download_podcasts()

        logs.logging_msg("transcribe podcasts")
        podcasts.transcribe_podcasts()

        logs.logging_msg("logout from podcastdb")
        podcastdb.logout()

        logs.logging_msg("END PROGRAM", "WARNING")

    else:
        print("logger.status:", logs.status)
        print("podcastdb.status:", podcastdb.status)
        exit(1)