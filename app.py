import os
import argparse
import asyncio
import threading
from flask import Flask, request, jsonify
from rss import get_rss, get_author, add_rss, remove_rss, get_log
# from rss_db import rss_db
from periodic_task import periodic_task

app = Flask(__name__)

# 创建一个 ArgumentParser 实例
parser = argparse.ArgumentParser()
# 添加一个名为 admin_key 的命令行参数
parser.add_argument("--admin_key", help="Admin key value", default="odinSay")
# 解析命令行参数
args = parser.parse_args()
# 获取 admin_key 的值
admin_key = args.admin_key


@app.after_request
def add_cors_headers(response):
    try:
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "access-control-allow-origin"
        )
    except Exception as e:
        response.headers["Access-Control-Allow-Origin"] = "*"
        print("add_cors_headers return error")
        pass
    return response


@app.route("/rss", methods=["GET"])
def get_rss_route():
    return get_rss(request)


@app.route("/author", methods=["GET"])
def get_author_route():
    return get_author(request)


@app.route("/new", methods=["GET"])
def add_rss_route():
    return add_rss(request, admin_key)


@app.route("/", methods=["GET"])
def default_return():
    return jsonify({"success": "site started"})


@app.route("/remove", methods=["GET"])
def remove_rss_route():
    return remove_rss(request, admin_key)


@app.route("/log", methods=["GET"])
def get_log_route():
    return get_log(request)

if __name__ == "__main__":
    if os.name == "nt":
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # rss_db.create_tables()
    # rss_db.close()
    # 创建一个线程，并将 run_periodic_task 函数作为目标
    # periodic_task()
        # 创建一个线程，并将 run_periodic_task 函数作为目标
    thread = threading.Thread(target=periodic_task)

    # 启动线程
    thread.start()

    app.run(host="0.0.0.0", port=5005)
    # 启动线程
