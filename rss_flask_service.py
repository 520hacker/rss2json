from flask import jsonify
from rss_db import RSSDatabase, LogDatabase
from rss_json import read_rss_list, write_rss_list


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
                "author": entry[2],
                "source": entry[3],
                "title": entry[4],
                "description": entry[5],
                "pubDate": entry[6],
                "enclosure": entry[7],
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
                "author": entry[3],
                "link": entry[4],
                "title": entry[5],
                "description": entry[6],
                "pubDate": entry[7],
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

    write_rss_list(rss_list)

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
    write_rss_list(rss_list)

    rss_db = RSSDatabase()
    rss_db.remove_rss_from_db(url)
    rss_db.close()

    return jsonify({"success": "RSS address removed successfully"})


def get_log(request):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    log_db = LogDatabase()
    total_count = log_db.get_log_count_from_db()
    log_entries = log_db.get_log_list_from_db(per_page, page)
    log_db.close()

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
