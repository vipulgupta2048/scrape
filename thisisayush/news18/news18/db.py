import psycopg2
from settings import DB_INFO, logger

class NewsDatabase():

    connect_str = "dbname='"+DB_INFO['name']+"' \
                    user='"+DB_INFO['user']+"' \
                    host='"+DB_INFO['host']+"' \
                    password='"+DB_INFO['password']+"'"

    site_table_name = "sites"
    item_table_name = "items"

    site_table = "CREATE TABLE IF NOT EXISTS "+site_table_name+"(\
                    id SERIAL PRIMARY KEY,\
                    site_name TEXT NOT NULL UNIQUE,\
                    site_url TEXT NOT NULL \
                    );"

    insert_site_str = "INSERT INTO "+site_table_name+"\
                        (site_name, site_url) VALUES (%s, %s);"

    item_table = "CREATE TABLE IF NOT EXISTS "+item_table_name+"(\
                    id SERIAL PRIMARY KEY,\
                    title TEXT NOT NULL, \
                    url TEXT UNIQUE NOT NULL, \
                    description TEXT, \
                    image TEXT, \
                    site INT NOT NULL, \
                    FOREIGN KEY(site) REFERENCES sites(id)\
                    ON DELETE CASCADE\
                    );"

    insert_item_str = "INSERT INTO "+item_table_name+"\
                        (title, url, description, image, site) \
                        VALUES(%s, %s, %s, %s, %s);"
    def connect(self):
        try:
            self.conn = psycopg2.connect(self.connect_str)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logger.debug(__name__+" Connected to Database")
            self.initilaize()
            return self.cursor
        except Exception as e:
            logger.critical(__name__+" Database Connection Error!"+str(e))

        return None

    def initilaize(self):
        try:
            # Create Tables
            self.cursor.execute(self.site_table)
            self.cursor.execute(self.item_table)
            #Commit
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(__name__+" Database Initilaization Error "+str(e))
            return False

    def getSiteId(self, site_name):
        logger.debug(__name__+" Searching Database for "+ site_name)
        sql = "SELECT id FROM "+self.site_table_name+" WHERE site_name = '"+site_name+"' LIMIT 1;"
        cur = self.connect()
        cur.execute(sql)
        if cur.rowcount != 0:
            site_id = cur.fetchone()[0]
            logger.debug("Found "+site_name+" at id: "+str(site_id))
            return site_id
        else:
            return False

    def getUrlsScraped(self, site_id):
        if site_id == False:
            return []
        try:
            sql = "SELECT url FROM "+self.item_table_name+" WHERE site= %s"
            cur = self.connect()
            cur.execute(sql, (site_id,))
            urls_parsed = []
            for url in cur.fetchall():
                urls_parsed.append(url[0])
            cur.close()
            return urls_parsed
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
        return []

    def urlExists(self, url):
        try:
            sql = "SELECT url FROM "+self.item_table_name+" WHERE url= %s"
            cur = self.connect()
            cur.execute(sql, (url,))
            rows = cur.rowcount
            self.conn.close()
            if rows > 0:
                return True
            else:
                return False
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
        return False
