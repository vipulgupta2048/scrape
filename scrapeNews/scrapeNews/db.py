import psycopg2
from psycopg2.extras import DictCursor
from .settings import DB_INFO, logger

class DatabaseManager(object):

    connect_str = "dbname='"+DB_INFO['name']+"' \
                    user='"+DB_INFO['user']+"' \
                    host='"+DB_INFO['host']+"' \
                    password='"+DB_INFO['password']+"'"
    conn = None
    endOnDel = True

    site_table_name = "site_table"
    item_table_name = "item_table"
    logs_table_name = "log_table"

    site_table = "CREATE TABLE IF NOT EXISTS "+site_table_name+"(\
                    id SERIAL PRIMARY KEY,\
                    site_name VARCHAR NOT NULL UNIQUE,\
                    site_url VARCHAR NOT NULL,\
                    spider_name VARCHAR NOT NULL UNIQUE \
                    );"

    insert_site_str = "INSERT INTO "+site_table_name+"\
                        (site_name, site_url, spider_name) VALUES (%s, %s, %s) RETURNING id;"

    item_table = "CREATE TABLE IF NOT EXISTS "+item_table_name+"(\
                    id SERIAL PRIMARY KEY,\
                    title VARCHAR NOT NULL, \
                    link VARCHAR UNIQUE NOT NULL, \
                    content TEXT NOT NULL, \
                    image VARCHAR NOT NULL, \
                    newsDate timestamptz NOT NULL, \
                    datescraped timestamptz NOT NULL, \
                    site_id SMALLINT NOT NULL, \
                    log_id INT NOT NULL, \
                    FOREIGN KEY(site_id) REFERENCES "+site_table_name+"(id) \
                    ON DELETE CASCADE, \
                    FOREIGN KEY(log_id) REFERENCES "+logs_table_name+"(id) \
                    ON DELETE NO ACTION \
                    );"

    insert_item_str = "INSERT INTO "+item_table_name+"\
                        (title, link, content, image, newsDate, datescraped,  site_id, log_id) \
                        VALUES(%s, %s, %s, %s, %s, NOW(), %s, %s) RETURNING id;"

    logs_table = "CREATE TABLE IF NOT EXISTS "+logs_table_name+"(\
                    id SERIAL PRIMARY KEY, \
                    site INT NOT NULL, \
                    start_time timestamptz NOT NULL DEFAULT NOW(), \
                    end_time timestamptz, \
                    urls_parsed INT DEFAULT 0, \
                    urls_scraped INT DEFAULT 0, \
                    urls_dropped INT DEFAULT 0, \
                    urls_stored INT DEFAULT 0, \
                    shutdown_reason VARCHAR DEFAULT 0, \
                    job_id VARCHAR DEFAULT 0, \
                    FOREIGN KEY(site) REFERENCES "+site_table_name+"(id) \
                    ON DELETE CASCADE \
                    );"

    def __init__(self, connection = None, endOnDel = True):
        if connection == None:
            self.connect()
        else:
            self.conn = connection.conn
            self.cursor = connection.cursor
            self.endOnDel = endOnDel

    def connect(self):
        if self.conn != None:
            if self.conn.closed == 0:
                return self.cursor
        try:
            self.conn = psycopg2.connect(self.connect_str)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
            logger.debug(__name__+" Connected to Database")
            self.initilaize()
            return self.cursor
        except Exception as e:
            logger.critical(__name__+" Database Connection Error!"+str(e))

        return None

    def initilaize(self):
        try:
            if self.connect() == None:
                return False
            # Create Tables
            self.cursor.execute(self.site_table)
            self.cursor.execute(self.logs_table)
            self.cursor.execute(self.item_table)
            #Commit
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(__name__+" Database Initilaization Error "+str(e))
            return False

    def getSiteId(self, site_name):
        if self.connect() == None:
            return False
        logger.debug(__name__+" Searching Database for "+ site_name)
        sql = "SELECT id FROM "+self.site_table_name+" WHERE site_name = %s LIMIT 1;"
        cur = self.cursor
        cur.execute(sql, (site_name,))
        if cur.rowcount != 0:
            site_id = cur.fetchone()['id']
            logger.debug("Found "+site_name+" at id: "+str(site_id))
            return site_id
        else:
            return False

    def getUrlsScraped(self, site_id):
        if site_id == False:
            return []
        try:
            if self.connect() == None:
                return False
            sql = "SELECT link FROM "+self.item_table_name+" WHERE site= %s"
            cur = self.cursor
            cur.execute(sql, (site_id,))
            urls_parsed = []
            for url in cur.fetchall():
                urls_parsed.append(url['url'])
            return urls_parsed
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
        return []

    def urlExists(self, url):
        try:
            if self.connect() == None:
                return False
            sql = "SELECT link FROM "+self.item_table_name+" WHERE link= %s"
            cur = self.cursor
            cur.execute(sql, (url,))
            rows = cur.rowcount
            if rows > 0:
                return True
            else:
                return False
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
        return False

    def __del__(self):
        if self.conn != None and self.endOnDel == True:
            self.conn.close()
            self.conn = None


class LogsManager(object):
    dbase = None

    def __init__(self, connection = None):
        if connection == None:
            self.dbase = DatabaseManager()
        else:
            self.dbase = connection

    def start_log(self, site, job = None):
        try:
            if self.dbase.connect() == None:
                return False
            if job == None:
                job = ""
            sql = "INSERT INTO "+self.dbase.logs_table_name+"(site, start_time, job_id) VALUES (%s, NOW(), %s) RETURNING id"
            cur = self.dbase.cursor
            cur.execute(sql, (site,job))
            log_id = cur.fetchone()['id']
            return log_id
        except Exception as e:
           logger.error(__name__+" DATABASE ERROR: "+str(e))
           return False

    def update_log(self, log_id, url_stats):
        """
        log_id (str): Returned from start_log
        url_stats (Dictionary): {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored' : 0}
        reason (str): String
        """

        try:
            if self.dbase.connect() == None:
                return False
            sql = "UPDATE "+self.dbase.logs_table_name+" \
                  SET urls_parsed = %s, urls_scraped = %s, \
                  urls_dropped = %s, urls_stored = %s WHERE id = %s"
            self.dbase.cursor.execute(sql, (url_stats['parsed'], url_stats['scraped'], url_stats['dropped'], url_stats['stored'], log_id))
            self.dbase.conn.commit()
            return True
        except Exception as e:
            logger.error(__name__ + " DATABASE ERROR: " + str(e))
            return False

    def end_log(self, log_id, url_stats, reason):
        """
        log_id (str): Returned from start_log
        url_stats (Dictionary): {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
        reason (str): String
        """
        try:
            if self.dbase.connect() == None:
                return False
            sql = "UPDATE "+self.dbase.logs_table_name+" \
                   SET end_time = NOW(), urls_parsed = %s, urls_scraped = %s, \
                   urls_dropped = %s, urls_stored = %s, shutdown_reason = %s WHERE id = %s"
            cur = self.dbase.cursor
            cur.execute(sql, (url_stats['parsed'], url_stats['scraped'], url_stats['dropped'], url_stats['stored'], reason, log_id,))
            self.dbase.conn.commit()
            return True
        except Exception as e:
            self.dbase.conn.rollback()
            logger.error(__name__+" DATABASE ERROR: "+str(e))
            return False

    def get_logs(self, site_id):
        try:
            if self.dbase.connect() == None:
                return False
            sql = "SELECT * FROM "+self.dbase.logs_table_name+" WHERE site = %s "
            cur = self.dbase.cursor
            cur.execute(sql, (site_id,))
            return cur.fetchall()
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
            return False

    def get_log(self, log_id):
        try:
            if self.dbase.connect() == None:
                return False
            sql = "SELECT * FROM "+self.dbase.logs_table_name+" WHERE id = %s"
            cur = self.dbase.cursor
            cur.execute(sql, (log_id,))
            return cur.fetchone()
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
            return False
    def __del__(self):
        del self.dbase

class ConnectionManager(object):

    connection = None

    def __init__(self, connection):
        self.connection = connection

    def checkConnection(self):
        try:
            if self.connection.conn == None:
                self.reconnect()
                if self.connection.conn == None:
                   return False
                else:
                   return True
            elif self.connection.conn.closed != 0:
                self.reconnect()
                if self.connection.conn == None:
                    return False
                else:
                    return True
            else:
                return True

        except NameError as e:
            return False
        except Exception as e:
            logger.error(__name__+" Unhandled: " + str(e) )

    def reconnect(self):
        logger.error(__name__+" Closed Connection Detected.. trying to connect...")
        max_tries = 3
        curr_tries = 0
        while curr_tries < max_tries:
            curr_tries += 1
            if self.connection.conn != None:
                if self.connection.conn.closed == 0:
                    break
            logger.error(__name__ + " Trying Connecting to Database"+str(curr_tries)+"/"+str(max_tries))
            self.connection.connect()
        if self.connection.conn == None or self.connection.conn.closed != 0:
            return False
        else:
            return True

