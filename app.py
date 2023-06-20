import os
import asyncio
import threading
from rss_periodic_task import periodic_task
from rss_flask import app

if __name__ == "__main__":
    if os.name == "nt":
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    thread = threading.Thread(target=periodic_task)

    # 启动线程
    thread.start()
    # 启动WEB
    app.run(host="0.0.0.0", port=5005)
