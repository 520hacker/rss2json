import argparse
from flask import Flask, request, jsonify
from rss_flask_service import get_rss, get_author, add_rss, remove_rss, get_log

# from app import admin_key
# 创建一个 ArgumentParser 实例
parser = argparse.ArgumentParser()
# 添加一个名为 admin_key 的命令行参数
parser.add_argument("--admin_key", help="Admin key value", default="odinSay")
# 解析命令行参数
args = parser.parse_args()
# 获取 admin_key 的值
admin_key = args.admin_key

app = Flask(__name__)


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
