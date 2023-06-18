import time
import threading
from rss import process_all_rss

lockObject = threading.Lock() 

# def start_periodic_task():
#     thread = threading.Thread(target=periodic_task)
#     thread.start()

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

# thread = threading.Thread(target=periodic_task)
# thread.start()
