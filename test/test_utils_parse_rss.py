import pytest
import dotenv
import os
from src.utils_parse_rss import ParseRSS


dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")


def test_main():
    if DEBUG == '4':
        assert True == True
    
    else:
        assert False