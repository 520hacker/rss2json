import json

def unique(a):
    # 创建一个集合用于存储已经出现过的rss值
    seen_rss = set()
    # 创建一个新的列表用于存储去重后的元素
    unique_a = []
    # 遍历原始列表a中的元素
    for item in a:
        rss = item["rss"]
        # 如果rss值没有出现过，则将该元素添加到去重后的列表中，并将rss添加到已经出现过的集合中
        if rss not in seen_rss:
            unique_a.append(item)
            seen_rss.add(rss)
    # 打印去重后的列表unique_a
    return unique_a


def read_rss_list():
    with open("rss.json", "r") as file:
        rss_list = json.load(file)
    return unique(rss_list)

def write_rss_list(rss_list):
    with open("rss.json", "w") as file:
        json.dump(rss_list, file)