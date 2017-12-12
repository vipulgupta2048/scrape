import psycopg2

class Database(object):

    conn = None 
    cursor = None
    create_table_item = "CREATE TABLE IF NOT EXISTS data_table (\
                  id SERIAL NOT NULL PRIMARY KEY, \
                  title TEXT NOT NULL,\
                  link TEXT NOT NULL,\
                  newsdate TEXT NOT NULL,\
                  content TEXT NOT NULL,\
                  image TEXT NOT NULL\
                  );"
    
    table_item = "INSERT INTO data_table(title, link, newsdate, content, image) \
                VALUES(%s, %s, %s, %s, %s);"
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(database="test", user="postgres", password="scrapy", host="localhost")
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
    


            