import os
import json
import sqlite3
import threading
import time
import feedparser
import calendar
import argparse
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
lockObject = threading.Lock()

# 创建一个 ArgumentParser 实例
parser = argparse.ArgumentParser()
# 添加一个名为 admin_key 的命令行参数
parser.add_argument('--admin_key', help='Admin key value', default='odinSay')
# 解析命令行参数
args = parser.parse_args()
# 获取 admin_key 的值
admin_key = args.admin_key

# 将pubDate转换为timestamp，如果转换失败则使用1天前的当前时间的timestamp值
def get_timestamp(pubDate):
    try:
        pubDate_time = time.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %z")
        # print(pubDate_time)
        pubDate_timestamp = calendar.timegm(pubDate_time)
        # print(pubDate_timestamp)
        return int(pubDate_timestamp)
    except:
        previous_day = get_current_timestamp() - (24 * 60 * 60)
        return previous_day

# 获取当前时间的timestamp
def get_current_timestamp():
    now = time.time()
    return int(now)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rss
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 link TEXT UNIQUE,
                 source TEXT,
                 title TEXT,
                 description TEXT,
                 pubDate INTEGER,
                 enclosure TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS source
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 rss TEXT UNIQUE,
                 link TEXT,
                 title TEXT,
                 description TEXT,
                 pubDate INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 time TEXT,
                 result TEXT)''')
    conn.commit()
    conn.close()

# 读取rss.json文件获取RSS地址列表
def read_rss_list():
    with open('rss.json', 'r') as file:
        rss_list = json.load(file)
    return rss_list

# 保存RSS内容到数据库
def save_rss_to_db(link, source, title, description, pubDate, enclosure):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rss WHERE link=?", (link,))
    existing_entry = c.fetchone()
    if existing_entry:
        # 如果已经存在相同的link值，则不进行插入操作
        return
    c.execute("INSERT INTO rss (link, source, title, description, pubDate, enclosure) VALUES (?, ?, ?, ?, ?, ?)",
              (link, source, title, description, pubDate, enclosure))
    conn.commit()
    conn.close()

# 保存已遍历的RSS地址到数据库
def save_source_to_db(rss, link, title, description, pubDate):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT * FROM source WHERE rss=?", (rss,))
    existing_entry = c.fetchone()
    if existing_entry:
        # 如果已经存在相同的link值，则不进行插入操作
        return
    c.execute("INSERT INTO source (rss, link, title, description, pubDate) VALUES (?, ?, ?, ?, ?)",
              (rss, link, title, description, pubDate))
    conn.commit()
    conn.close()


# 保存日志到数据库
def save_log_to_db(time, result):
    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("INSERT INTO log (time, result) VALUES (?, ?)", (time, result))
    conn.commit()
    conn.close()

# 处理单个RSS地址的请求
def process_rss(url, rss):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            rss_content = response.text
            rss_feed = feedparser.parse(rss_content)
            # print(rss_feed[0]) 

            # 获取 channel 的信息
            channel = rss_feed['feed']
            title = channel['title']
            # print(title)
            link = channel['link']
            # print(link)
            description = channel['description']
            # print(description)
            pubDate = channel['published'] 
            # print(pubDate)
            save_source_to_db(url, link, title, description, get_timestamp(pubDate))

            for entry in rss_feed.entries:
                link = entry.get('link', '')
                title = entry.get('title', '')
                description = entry.get('description', '')
                pubDate = entry.get('published', '')
                enclosure = entry.get('enclosure', '')
                pubDate_timestamp = get_timestamp(pubDate)
                save_rss_to_db(link, url, title, description, pubDate_timestamp, enclosure)

            print(f"Successfully processed RSS: {url}")
            save_log_to_db(time.strftime("%Y-%m-%d %H:%M:%S"), f"Successfully processed RSS: {url}")
        else:
            save_log_to_db(time.strftime("%Y-%m-%d %H:%M:%S"), f"Failed to connect to RSS: {url}")
            print(f"Failed to connect to RSS: {url}")
    except Exception as e:
        save_log_to_db(time.strftime("%Y-%m-%d %H:%M:%S"), f"Error processing RSS: {url}, {str(e)}")
        print(f"Error processing RSS: {url}, {str(e)}")

# 遍历所有的RSS地址
def process_all_rss():
    rss_list = read_rss_list()
    threads = []
    for rss in rss_list:
        url = rss
        t = threading.Thread(target=process_rss, args=(url, rss,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

# 启动时立即执行一次遍历
init_db()
process_all_rss()

# 定时执行遍历任务
def periodic_task():
    while True:
        if not lockObject.locked():
            lockObject.acquire()
            print("Periodic task started")
            process_all_rss()
            lockObject.release()
            print("Periodic task completed")
        time.sleep(300)

thread = threading.Thread(target=periodic_task)
thread.start()

# API: /rss
@app.route('/rss', methods=['GET'])
def get_rss():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    search = request.args.get('search', '')

    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM rss")
    total_count = c.fetchone()[0]

    c.execute("SELECT * FROM rss WHERE title LIKE ? OR description LIKE ? ORDER BY pubDate DESC",
              (f"%{search}%", f"%{search}%"))
    rss_entries = c.fetchall()

    rss_list = []
    for entry in rss_entries[(page-1)*per_page:page*per_page]:
        rss_list.append({
            'link': entry[1],
            'source': entry[2],
            'title': entry[3],
            'description': entry[4],
            'pubDate': entry[5],
            'enclosure': entry[6]
        })

    conn.close()

    return jsonify({
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'rss_list': rss_list
    })

# API: /author
@app.route('/author', methods=['GET'])
def get_author():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM source")
    total_count = c.fetchone()[0]

    c.execute("SELECT * FROM source LIMIT ? OFFSET ?", (per_page, (page-1)*per_page))
    author_entries = c.fetchall()

    author_list = []
    for entry in author_entries:
        author_list.append({
            'rss': entry[1],
            'link': entry[2],
            'title': entry[3],
            'description': entry[4],
            'pubDate': entry[5]
        })

    conn.close()

    return jsonify({
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'author_list': author_list
    })

# API: /new
@app.route('/new', methods=['GET'])
def add_rss():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'URL parameter is missing'})
    
    key = request.args.get('key', '')  # 获取 key 参数值
    if key != admin_key:  # 检查 key 参数值是否正确
        return jsonify({'error': 'Invalid key'})

    rss_list = read_rss_list()
    rss_exist = any(rss == url for rss in rss_list)
    if rss_exist:
        return jsonify({'error': 'RSS address already exists'})

    rss_list.append(url)
    with open('rss.json', 'w') as file:
        json.dump(rss_list, file)

    process_rss(url,"")
    return jsonify({'success': 'RSS address added successfully'})


@app.route('/', methods=['GET'])
def default_return():
    return jsonify({'success': 'site started'})

# API: /remove
@app.route('/remove', methods=['GET'])
def remove_rss():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'URL parameter is missing'})
    
    key = request.args.get('key', '')  # 获取 key 参数值
    if key != admin_key:  # 检查 key 参数值是否正确
        return jsonify({'error': 'Invalid key'})

    rss_list = read_rss_list()
    rss_not_exist = all(rss != url for rss in rss_list)
    if rss_not_exist:
        return jsonify({'error': 'RSS address does not exist'})

    if len(rss_list) == 1:
        return jsonify({'error': 'Only 1 RSS address left'})

    rss_list = [rss for rss in rss_list if rss != url]
    with open('rss.json', 'w') as file:
        json.dump(rss_list, file)

    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("DELETE FROM rss WHERE link IN (SELECT link FROM source WHERE rss=?)", (url,))
    c.execute("DELETE FROM source WHERE rss=?", (url,))
    conn.commit()
    conn.close()

    return jsonify({'success': 'RSS address removed successfully'})

# API: /log
@app.route('/log', methods=['GET'])
def get_log():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    conn = sqlite3.connect('rss.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM log")
    total_count = c.fetchone()[0]

    c.execute("SELECT * FROM log ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, (page-1)*per_page))
    log_entries = c.fetchall()

    log_list = []
    for entry in log_entries:
        log_list.append({
            'id': entry[0],
            'time': entry[1],
            'result': entry[2]
        })

    conn.close()

    return jsonify({
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'log_list': log_list
    })

if __name__ == '__main__':
    if os.name == 'nt':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    init_db()
    app.run(host='0.0.0.0', port=5005)
