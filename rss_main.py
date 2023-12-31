import json
import requests
import feedparser

from rss_db import RSSDatabase, get_timestamp
from rss_json import read_rss_list
from rss_fetch import fetch_json_logo, fetch_json_updates, fetch_rss_content
from rss_db_log import db_log_info
from rss_url import rss_to_channel_url


def get_resource_json(item_url, site_url, base_url, feeds_json):
    try:
        if feeds_json is None:
            feeds_json = []  # 或者根据需求设置一个空列表或其他默认值
        for entry in feeds_json:
            new_url = base_url + "/m/" + str(entry["id"])
            if item_url == new_url:
                images = entry["resourceList"]
                new_image_list = []
                for image in json.loads(images):
                    new_image_url = image["externalLink"]
                    if base_url != site_url:
                        new_image_url = new_image_url.replace(base_url, site_url)
                    new_image_list.append(
                        {"type": image["type"], "href": new_image_url}
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
        rss_content = fetch_rss_content(url)
        if rss_content != None: 
            rss_feed = feedparser.parse(rss_content)
            type = rss_item["type"]
            avatar = rss_item["avatar"]
            author = ""
            feeds_json = None

            channel = rss_feed["feed"]
            title = channel["title"]
            channel_link = channel["link"]
            site_url = rss_to_channel_url(url)
            description = channel["description"]
            pubDate = channel["published"]

            try:
                if type == "1":
                    feeds_json = fetch_json_updates(url)
                    author = get_author_json(feeds_json)
                    if avatar == "":
                        avatar = fetch_json_logo(url)

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
                site_url,
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
                    new_image_list = get_resource_json(
                        link, site_url, channel_link, feeds_json
                    )
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
                    link, author, url, title, description, pubDate_timestamp, enclosure
                )

            rss_db.close()
            db_log_info(f"Successfully processed RSS: {url}")

        else:
            db_log_info(f"Failed to connect to RSS: {url}")
    except Exception as e:
        db_log_info(f"Error processing RSS: {url}, {str(e)}")


def process_all_rss():
    rss_list = read_rss_list()
    for rss_item in rss_list:
        try:
            process_rss(rss_item["rss"], rss_item)
        except Exception as ex:
            db_log_info(f"Error process_rss: {rss_item['rss']}, {str(ex)}")

