import dotenv
import os
from logs import Logger


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logger = Logger()
    if logger:
        print(logger)