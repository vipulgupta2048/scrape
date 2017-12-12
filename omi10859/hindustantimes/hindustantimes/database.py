import psycopg2

class Database(object):

    def __init__(self):
        self.connect()
    conn = None 
    cursor = None
    create_table_item = "CREATE TABLE IF NOT EXISTS data_table (\
                  id SERIAL NOT NULL PRIMARY KEY, \
                  title TEXT NOT NULL,\
                  link TEXT NOT NULL,\
                  newsdate TIMESTAMP,\
                  content TEXT NOT NULL,\
                  image TEXT NOT NULL\
                  );"
    
    table_item = "INSERT INTO data_table(title, link, newsdate, content, image) \
                VALUES(%s, %s, %s, %s, %s);"
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(database="test", user="postgres", password="scrapy", host="localhost")
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            self.Create()
            print("Connection Established")
            return self.cursor
        except Exception as e:
            print("database connection error: "+str(e))
        return None

    def Create(self):
        try:
            self.cursor.execute(self.create_table_item)
            self.conn.commit()
            return True 
        except Exception as e:
            print(__name__ + " Unhandled: " + str(e))
            self.conn.rollback()
            return False
    
    def url(self, url):
        try:
            sql = 'SELECT link FROM data_table WHERE link= %s'
            cur = self.connect()
            cur.execute(sql,(url,))
            rows = cur.rowcount
            self.conn.close()
            if rows > 0:
                return True
            else:
                return False
        except Exception as e:
            print("not able to get url from table"+str(e))
            return False 

            