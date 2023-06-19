import re

def rss_to_channel_url(url):
    # 匹配 {prefix}/u/{id}/rss.xml
    pattern = r"^(.*)/u/(\d+)/rss\.xml$"
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    else:
        return None


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


def rss_to_avatar_url(url):
    # 匹配 {prefix}/u/{id}/rss.xml
    pattern = r"^(.*)/u/(\d+)/rss\.xml$"
    match = re.match(pattern, url)
    if match:
        prefix = match.group(1)
        memo_url = f"{prefix}/api/status"
        return memo_url
    else:
        return None
