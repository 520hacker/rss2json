import sqlite3
import time
import calendar


class RSSDatabase:
    def __init__(self):
        self.conn = None
        self.c = None
        self.connect()

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect("rss.db")
            self.c = self.conn.cursor()
            self.c.execute("PRAGMA journal_mode=WAL")
            self.create_tables()

    def create_tables(self):
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS rss
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     link TEXT UNIQUE,
                     author TEXT,
                     source TEXT,
                     title TEXT,
                     description TEXT,
                     pubDate INTEGER,
                     enclosure TEXT)"""
        )
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS source
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     rss TEXT UNIQUE,
                     avatar TEXT,
                     author TEXT,
                     link TEXT,
                     title TEXT,
                     description TEXT,
                     pubDate INTEGER)"""
        )
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     time TEXT,
                     result TEXT)"""
        )
        self.conn.commit()

    def save_rss_to_db(self, link, author, source, title, description, pubDate, enclosure):
        self.connect()
        self.c.execute("SELECT * FROM rss WHERE link=?", (link,))
        existing_entry = self.c.fetchone()
        if existing_entry:
            return
        self.c.execute(
            "INSERT INTO rss (link, author, source, title, description, pubDate, enclosure) VALUES (?,?, ?, ?, ?, ?, ?)",
            (link, author, source, title, description, pubDate, enclosure),
        )
        self.conn.commit()

    def save_source_to_db(self, rss, avatar, author, link, title, description, pubDate):
        self.connect()
        self.c.execute("SELECT * FROM source WHERE rss=?", (rss,))
        existing_entry = self.c.fetchone()
        if existing_entry:
            if avatar and existing_entry[1] != avatar:
                self.c.execute("UPDATE source SET avatar=? WHERE rss=?", (avatar, rss))
        else:
            self.c.execute(
                "INSERT INTO source (rss, avatar, author,link, title, description, pubDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rss, avatar, author, link, title, description, pubDate),
            )
        self.conn.commit()

    def save_log_to_db(self, time, result):
        self.connect()
        self.c.execute("INSERT INTO log (time, result) VALUES (?, ?)", (time, result))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.c = None

    def remove_rss_from_db(self, url):
        self.connect()
        self.c.execute(
            "DELETE FROM rss WHERE link IN (SELECT link FROM source WHERE rss=?)",
            (url,),
        )
        self.c.execute("DELETE FROM source WHERE rss=?", (url,))
        self.conn.commit()

    def get_log_count_from_db(self):
        self.connect()
        self.c.execute("SELECT COUNT(*) FROM log")
        return self.c.fetchone()[0]

    def get_log_list_from_db(self, per_page, page):
        self.connect()
        self.c.execute(
            "SELECT * FROM log ORDER BY id DESC LIMIT ? OFFSET ?",
            (per_page, (page - 1) * per_page),
        )
        return self.c.fetchall()

    def get_source_count_from_db(self):
        self.connect()
        self.c.execute("SELECT COUNT(*) FROM source")
        return self.c.fetchone()[0]

    def get_source_list_from_db(self, per_page, page):
        self.connect()
        self.c.execute(
            "SELECT * FROM source ORDER BY id DESC LIMIT ? OFFSET ?",
            (per_page, (page - 1) * per_page),
        )
        return self.c.fetchall()

    def get_count_from_db(self, search, source):
        self.connect()
        sql = "SELECT COUNT(*) FROM rss"
        params = []

        if search:
            sql += " WHERE (title LIKE ? OR description LIKE ?) "
            params.extend([f"%{search}%", f"%{search}%"])

        if source:
            if search:
                sql += " AND source = ?"
            else:
                sql += " WHERE source = ?"
            params.append(source)

        total_count = self.c.execute(sql, params).fetchone()[0]
        return total_count

    def get_list_from_db(self, search, source):
        self.connect()
        sql = "SELECT * FROM rss"
        params = []

        if search:
            sql += " WHERE (title LIKE ? OR description LIKE ? ) "
            params.extend([f"%{search}%", f"%{search}%"])
        if source:
            if search:
                sql += " AND source = ?"
            else:
                sql += " WHERE source = ?"
            params.append(source)

        sql += " ORDER BY pubDate DESC"

        rss_entries = self.c.execute(sql, params).fetchall()
        return rss_entries 


    # def execount(self, sql, objs):
    #     self.connect()
    #     self.c.execute(sql, objs)
    #     return self.c.fetchone()[0]

    # def execount(self, sql):
    #     self.connect()
    #     self.c.execute(sql)
    #     return self.c.fetchone()[0]

    # def execute(self, sql, objs):
    #     self.connect()
    #     self.c.execute(sql, objs)
    #     return self.c.fetchall()

    # def execute(self, sql):
    #     self.connect()
    #     self.c.execute(sql)
    #     return self.c.fetchall()


def get_timestamp(pubDate):
    try:
        pubDate_time = time.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %z")
        pubDate_timestamp = calendar.timegm(pubDate_time)
        return int(pubDate_timestamp)
    except:
        previous_day = get_current_timestamp() - (24 * 60 * 60)
        return previous_day


def get_current_timestamp():
    now = time.time()
    return int(now)
