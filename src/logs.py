from datetime import datetime, timedelta
import logging
import os


class Logs:
    def __init__(self):
        self.status = None # status == None > all right, status != None > error
        self.DEBUG = os.getenv("DEBUG")
        self.LOGS_PATH = os.getenv("LOGS_PATH")
        
        self.create_file()
        if not self.status: self.basicConfig()
        if not self.status: self.cleanup_log()


    def create_file(self):
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            os.makedirs(self.LOGS_PATH, exist_ok=True)
            self.log_filename = f"{self.LOGS_PATH}{date_str}.log"

        except Exception as e:
            if self.DEBUG != '4':
                self.status = f"Error in logging.py Logger.create_file(): {e}"
    

    def basicConfig(self):
        try:
            if self.DEBUG != '0':
                print("§§§§§§§§§§§§§§§§§§§§§§")
                print("§§§§§ DEBUG MODE §§§§§")
                print("§§§§§§§§§§§§§§§§§§§§§§")
                print("Debug mode: ", self.DEBUG)
                if self.DEBUG == '1':
                    logging.basicConfig(filename=self.log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                elif self.DEBUG == '2':
                    logging.basicConfig(filename=self.log_filename, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
                elif self.DEBUG == '3':
                    logging.basicConfig(filename=self.log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            
            else:
                logging.basicConfig(filename=self.log_filename, level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

        except Exception as e:
            self.status = f"Error in logging.py Logger.basicConfig(): {e}"


    def cleanup_log(self):
        retention_days = int(os.getenv('LOG_RETENTION_DAYS', '30'))
        self.logging_msg(f"retention_days: '{retention_days}'", 'DEBUG')
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        self.logging_msg(f"cutoff_date: '{cutoff_date}'", 'DEBUG')
        
        for log_file in os.listdir(self.LOGS_PATH):
            log_path = os.path.join(self.LOGS_PATH, log_file)
            if os.path.isfile(log_path):
                try:
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(log_path))
                    if file_mod_time < cutoff_date:
                        os.remove(log_path)
                        self.logging_msg(f"'{log_file}' deleted", 'DEBUG')
                    else:
                        self.logging_msg(f"'{log_file}' not deleted", 'DEBUG')

                except Exception as e:
                    self.logging_msg(f"Error deleting '{log_file}': {e}", 'WARNING')


    def logging_msg(self, msg, type='INFO')->bool:
        try:
            logger = logging.getLogger(__name__)
            # print(logging.getLevelName(logger.getEffectiveLevel()))

            type = type.upper()

            if type == 'INFO':
                logger.info(msg)
            elif type == 'DEBUG':
                logger.debug(msg)
            elif type == 'ERROR':
                logger.error(msg)
            elif type == 'WARNING':
                logger.warning(msg)
            elif type == 'CRITICAL':
                logger.critical(msg)
            elif type == 'SQL':
                if self.DEBUG == '3':
                    logger.info(msg)

            if self.DEBUG > '0':
                print(f"[{type}] {msg}")

            return True

        except Exception as e:
            print(f"Error in logging.py Logger.logging_msg(): {e}")
            return False