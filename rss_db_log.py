
import time
from rss_db import LogDatabase

def db_log_info(msg):
    print(f"{msg}")
    log_db = LogDatabase()
    log_db.save_log_to_db(
        time.strftime("%Y-%m-%d %H:%M:%S"), f"{msg}"
    )
    log_db.close()