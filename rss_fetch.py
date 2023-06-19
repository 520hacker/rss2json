import requests
import json
from rss_url import rss_to_memo_url, rss_to_avatar_url
from rss_json import read_rss_list, write_rss_list


def update_logo_to_json(url, avatar):
    rss_list = read_rss_list()
    for rss_item in rss_list:
        if rss_item["rss"] == url:
            rss_item["avatar"] = avatar
            write_rss_list(rss_list)
            break


def fetch_json_logo(url):
    try:
        asset_url = rss_to_avatar_url(url)
        response = requests.get(asset_url)
        response.raise_for_status()  # 检查响应状态码，如果不是200会抛出异常
        data = response.json()
        avatar = data["data"]["customizedProfile"]["logoUrl"]
        print(f"Successfully processed Avatar API: {url}")
        if avatar.startswith("/"):
            avatar = url + avatar
            
        update_logo_to_json(url, avatar)
        return avatar
    except requests.exceptions.RequestException as ex:
        print(f"Request failed: {ex}")
        raise  # 抛出异常以便更好地处理错误
    except Exception as ex:
        print(f"An error occurred: {ex}")
        raise  # 抛出异常以便更好地处理错误


def fetch_json_updates(url):
    try:
        url = rss_to_memo_url(url)
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
