import json
import requests
import time

# import threading
import feedparser
from flask import jsonify
from rss_db import RSSDatabase, get_timestamp


def read_rss_list():
    with open("rss.json", "r") as file:
        rss_list = json.load(file)
    return rss_list


def process_rss(url, rss_item):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            rss_content = response.text
            rss_feed = feedparser.parse(rss_content)

            avatar = rss_item["avatar"]
            channel = rss_feed["feed"]
            title = channel["title"]
            link = channel["link"]
            description = channel["description"]
            pubDate = channel["published"]
            rss_db = RSSDatabase()
            rss_db.save_source_to_db(
                url, avatar, link, title, description, get_timestamp(pubDate)
            )

            for entry in rss_feed.entries:
                link = entry.get("link", "")
                title = entry.get("title", "")
                description = entry.get("description", "")
                pubDate = entry.get("published", "")
                enclosure = ""

                try:
                    filtered_links = [
                        item for item in entry.links if item.get("type") != "text/html"
                    ]
                    enclosure = json.dumps(filtered_links)
                except Exception as ex:
                    pass

                pubDate_timestamp = get_timestamp(pubDate)
                rss_db.save_rss_to_db(
                    link, url, title, description, pubDate_timestamp, enclosure
                )

            print(f"Successfully processed RSS: {url}")
            rss_db.save_log_to_db(
                time.strftime("%Y-%m-%d %H:%M:%S"), f"Successfully processed RSS: {url}"
            )
            rss_db.close()

        else:
            rss_db = RSSDatabase()
            rss_db.save_log_to_db(
                time.strftime("%Y-%m-%d %H:%M:%S"), f"Failed to connect to RSS: {url}"
            )
            rss_db.close()

            print(f"Failed to connect to RSS: {url}")
    except Exception as e:
        rss_db = RSSDatabase()
        rss_db.save_log_to_db(
            time.strftime("%Y-%m-%d %H:%M:%S"), f"Error processing RSS: {url}, {str(e)}"
        )
        rss_db.close()

        print(f"Error processing RSS: {url}, {str(e)}")


def process_all_rss():
    rss_list = read_rss_list()
    # threads = []
    for rss_item in rss_list:
        url = rss_item["rss"]
        # t = threading.Thread(
        #     target=process_rss,
        #     args=(
        #         url,
        #         rss_item,
        #     ),
        # )
        # threads.append(t)
        # t.start()
        process_rss(url, rss_item)
    # for t in threads:
    #     t.join()


def get_rss(request):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search", "")
    source = request.args.get("source", "")

    rss_db = RSSDatabase()
    total_count = rss_db.get_count_from_db(search, source)
    rss_entries = rss_db.get_list_from_db(search, source)
    rss_db.close()

    rss_list = []
    for entry in rss_entries[(page - 1) * per_page : page * per_page]:
        rss_list.append(
            {
                "link": entry[1],
                "source": entry[2],
                "title": entry[3],
                "description": entry[4],
                "pubDate": entry[5],
                "enclosure": entry[6],
            }
        )

    return jsonify(
        {
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "rss_list": rss_list,
        }
    )


def get_author(request):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    rss_db = RSSDatabase()
    total_count = rss_db.get_source_count_from_db()
    author_entries = rss_db.get_source_list_from_db(per_page, page)
    rss_db.close()

    author_list = []
    for entry in author_entries:
        author_list.append(
            {
                "rss": entry[1],
                "avatar": entry[2],
                "link": entry[3],
                "title": entry[4],
                "description": entry[5],
                "pubDate": entry[6],
            }
        )

    return jsonify(
        {
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "author_list": author_list,
        }
    )


def add_rss(request, admin_key):
    avatar = request.args.get("avatar", "")
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "URL parameter is missing"})

    key = request.args.get("key", "")
    if key != admin_key:
        return jsonify({"error": "Invalid key"})

    rss_list = read_rss_list()
    rss_exist = any(rss_item["rss"] == url for rss_item in rss_list)

    if rss_exist:
        if avatar:
            for rss_item in rss_list:
                if rss_item["rss"] == url:
                    rss_item["avatar"] = avatar
                    break
        else:
            return jsonify({"error": "RSS address already exists"})
    else:
        new_record = {"rss": url, "avatar": avatar}
        rss_list.append(new_record)

    with open("rss.json", "w") as file:
        json.dump(rss_list, file)

    process_rss(url, new_record)
    return jsonify({"success": "RSS address added successfully"})


def remove_rss(request, admin_key):
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "URL parameter is missing"})

    key = request.args.get("key", "")
    if key != admin_key:
        return jsonify({"error": "Invalid key"})

    rss_list = read_rss_list()
    rss_not_exist = all(rss_item["rss"] != url for rss_item in rss_list)
    if rss_not_exist:
        return jsonify({"error": "RSS address does not exist"})

    if len(rss_list) == 1:
        return jsonify({"error": "Only 1 RSS address left"})

    rss_list = [rss_item for rss_item in rss_list if rss_item["rss"] != url]
    with open("rss.json", "w") as file:
        json.dump(rss_list, file)

    rss_db = RSSDatabase()
    rss_db.remove_rss_from_db(url)
    rss_db.close()

    return jsonify({"success": "RSS address removed successfully"})


def get_log(request):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    rss_db = RSSDatabase()
    total_count = rss_db.get_log_count_from_db()
    log_entries = rss_db.get_log_list_from_db(per_page, page)
    rss_db.close()

    log_list = []
    for entry in log_entries:
        log_list.append({"id": entry[0], "time": entry[1], "result": entry[2]})

    return jsonify(
        {
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "log_list": log_list,
        }
    )
