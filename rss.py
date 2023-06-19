import json
import requests
import time
import re
import feedparser

# import markdown
from flask import jsonify
from rss_db import RSSDatabase, LogDatabase, get_timestamp


def read_rss_list():
    with open("rss.json", "r") as file:
        rss_list = json.load(file)
    return rss_list


def rss_to_memo_url(url):
    # 匹配 {prefix}/u/{id}/rss.xml
    pattern = r"^(.*)/u/(\d+)/rss\.xml$"
    match = re.match(pattern, url)
    if match:
        prefix = match.group(1)
        id = match.group(2)
        # 构造 {prefix}/api/memo?creatorId={id}&rowStatus=NORMAL&limit=50
        memo_url = f"{prefix}/api/memo?creatorId={id}&rowStatus=NORMAL&limit=50"
        return memo_url
    else:
        return None


def fetch_json_logo(url):
    try:
        response = requests.get(url + "/api/status")
        response.raise_for_status()  # 检查响应状态码，如果不是200会抛出异常
        data = response.json()
        avatar = data["data"]["customizedProfile"]["logoUrl"]
        print(f"Successfully processed Avatar API: {url + '/api/status'}")
        if avatar.startswith("/"):
            avatar = url + avatar
        return avatar
    except requests.exceptions.RequestException as ex:
        print(f"Request failed: {ex}")
        raise  # 抛出异常以便更好地处理错误
    except Exception as ex:
        print(f"An error occurred: {ex}")
        raise  # 抛出异常以便更好地处理错误


def fetch_json_updates(url):
    try:
        # 发起GET请求获取API接口返回的JSON数据
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # 收集需要的数据
            result = []
            for item in data["data"]:
                # 处理content字段，将Markdown转换为HTML
                # content_html = markdown.markdown(item["content"])

                # 处理resourceList字段，转换为JSON字符串
                resource_list = json.dumps(item["resourceList"])

                # 收集数据
                result.append(
                    {
                        "id": item["id"],
                        "creatorName": item["creatorName"],
                        "resourceList": resource_list,
                    }
                )
            print(f"Successfully processed JSON API: {url}")
            return result
        return None
    except Exception as ex:
        print(f"格式化jsonfeeds发生了错误${ex}")
        pass
    return None


def get_resource_json(item_url, base_url, feeds_json):
    try:
        for entry in feeds_json:
            new_url = base_url + "/m/" + str(entry["id"])
            if item_url == new_url:
                images = entry["resourceList"]
                new_image_list = []
                for image in json.loads(images):
                    new_image_list.append(
                        {"type": image["type"], "href": image["externalLink"]}
                    )
                return new_image_list
        return []
    except Exception as ex:
        print(f"获取new_image_list发生了错误${ex}")
        return []


def get_author_json(feeds_json):
    for entry in feeds_json:
        return entry["creatorName"]
    return ""


def process_rss(url, rss_item):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            rss_content = response.text
            rss_feed = feedparser.parse(rss_content)
            type = rss_item["type"]
            avatar = rss_item["avatar"]
            author = ""
            feeds_url = ""
            feeds_json = None

            channel = rss_feed["feed"]
            title = channel["title"]
            channel_link = channel["link"]
            description = channel["description"]
            pubDate = channel["published"]

            try:
                if type == "1":
                    feeds_url = rss_to_memo_url(url)
                    feeds_json = fetch_json_updates(feeds_url)
                    author = get_author_json(feeds_json)
                    if avatar == "":
                        avatar = fetch_json_logo(channel_link)
                        
            except Exception as ex:
                print(f"获取json feeds发生了错误${ex}")
                pass

            if avatar == "":
                avatar = "https://memosfile.qiangtu.com/picgo/assets/2023/06/18202306_18110103.png?x-oss-process=image/resize,h_50,w_50"

            rss_db = RSSDatabase()
            rss_db.save_source_to_db(
                url,
                avatar,
                author,
                channel_link,
                title,
                description,
                get_timestamp(pubDate),
            )

            for entry in rss_feed.entries:
                link = entry.get("link", "")
                title = entry.get("title", "")
                description = entry.get("description", "")
                pubDate = entry.get("published", "")
                enclosure = ""

                try:
                    new_image_list = get_resource_json(link, channel_link, feeds_json)
                    if isinstance(new_image_list, list) and len(new_image_list) > 0:
                        filtered_links = new_image_list
                    else:
                        filtered_links = [
                            item
                            for item in entry.links
                            if item.get("type") != "text/html"
                        ]
                    enclosure = json.dumps(filtered_links)
                except Exception as ex:
                    print(f"格式化enclosure发生了错误${ex}")
                    pass

                pubDate_timestamp = get_timestamp(pubDate)
                rss_db.save_rss_to_db(
                    link, url, author, title, description, pubDate_timestamp, enclosure
                )

            rss_db.close()
            log_db = LogDatabase()
            print(f"Successfully processed RSS: {url}")
            log_db.save_log_to_db(
                time.strftime("%Y-%m-%d %H:%M:%S"), f"Successfully processed RSS: {url}"
            )
            log_db.close()

        else:
            log_db = LogDatabase()
            log_db.save_log_to_db(
                time.strftime("%Y-%m-%d %H:%M:%S"), f"Failed to connect to RSS: {url}"
            )
            log_db.close()

            print(f"Failed to connect to RSS: {url}")
    except Exception as e:
        log_db = LogDatabase()
        log_db.save_log_to_db(
            time.strftime("%Y-%m-%d %H:%M:%S"), f"Error processing RSS: {url}, {str(e)}"
        )
        log_db.close()

        print(f"Error processing RSS: {url}, {str(e)}")


def process_all_rss():
    rss_list = read_rss_list()
    for rss_item in rss_list:
        url = rss_item["rss"]
        process_rss(url, rss_item)


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
                "author": entry[3],
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
