import time
import threading
from rss_main import process_all_rss

lockObject = threading.Lock()


# 定时执行遍历任务
def periodic_task():
    while True:
        if not lockObject.locked():
            lockObject.acquire()
            print("Periodic task started")
            process_all_rss()
            lockObject.release()
            print("Periodic task completed")
        time.sleep(300)
