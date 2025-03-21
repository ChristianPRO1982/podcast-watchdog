import dotenv
from src.logs import Logs
from src.utils_sqlite import PodcastDB
from src.utils_parse_rss import ParseRSS
from src.utils_podcast import Podcasts


dotenv.load_dotenv(override=True)


def main()->bool:
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

        logs.logging_msg("summarize podcasts")
        podcasts.summarize_podcasts()

        logs.logging_msg("Update published_int")
        podcasts.update_published_int()

        logs.logging_msg("logout from podcastdb")
        podcastdb.logout()

        logs.logging_msg("END PROGRAM", "WARNING")

        return True

    else:
        print("logger.status:", logs.status)
        print("podcastdb.status:", podcastdb.status)
        return False


if __name__ == "__main__":
    main()