import pytest
import dotenv
import os
from src.main import main


dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")


def test_main():
    if DEBUG == '4':
        assert main() == True
    
    else:
        assert False