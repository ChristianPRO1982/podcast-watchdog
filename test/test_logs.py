import pytest
import dotenv
import os
from src.logs import Logs


dotenv.load_dotenv(override=True)
DEBUG = os.getenv("DEBUG")
logs = Logs()


def test_status():
    if DEBUG == '4':
        if not logs.status:
            assert True
    
    else:
        assert False

def test_msg():
    if DEBUG == '4':
        assert logs.logging_msg("test") == True
        assert logs.logging_msg("test", 'INFO') == True
        assert logs.logging_msg("test", 'DEBUG') == True
        assert logs.logging_msg("test", 'ERROR') == True
        assert logs.logging_msg("test", 'WARNING') == True
        assert logs.logging_msg("test", 'CRITICAL') == True
        assert logs.logging_msg("test", 'SQL') == True
    
    else:
        assert False