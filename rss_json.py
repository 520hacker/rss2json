import json

def read_rss_list():
    with open("rss.json", "r") as file:
        rss_list = json.load(file)
    return rss_list

def write_rss_list(rss_list):
    with open("rss.json", "w") as file:
        json.dump(rss_list, file)