## Enter the Details Here
PASSWORD = 'simple'

SPIDER_DETAILS = [
#{'site_id':'','site_name':'','site_url':''}
{'site_id':101,'site_name':'Indian Express','site_url':'http://indianexpress.com/section/technology/'},
{'site_id':102,'site_name':'India TV','site_url':'http://www.indiatvnews.com/business/tech/'},
{'site_id':103,'site_name':'Time','site_url':'http://time.com/section/tech/'}
]

# Setting Up Database with imformation as given above
import psycopg2

class setupDB:

    def createDatabase(PASSWORD):
        try:
            connection = psycopg2.connect(host='localhost', user='scrapeuser', database='postgres', password=PASSWORD)
            cursor = connection.cursor()
            connection.autocommit = True
            cursor.execute('CREATE DATABASE scraped_news')
            cursor.close()
            connection.close()
            setupDB.createTables(PASSWORD)
        except psycopg2.ProgrammingError as Error:
            setupDB.createTables(PASSWORD)
        except Exception as Error:
            print ("Error 101: ", Error)


    def createTables(PASSWORD):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS site_table (
                id SMALLINT PRIMARY KEY,
                site_name VARCHAR(255) NOT NULL,
                site_url VARCHAR(255) NOT NULL
                )
            """,
            """
            CREATE TABLE IF NOT EXISTS news_table (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content VARCHAR(255) NOT NULL,
                link VARCHAR(255) NOT NULL,
                image VARCHAR(255) NOT NULL,
                newsDate VARCHAR(255) NOT NULL,
                site_id SMALLINT NOT NULL REFERENCES site_table (id)
            )
            """
            )
        try:
            connection = psycopg2.connect(host='localhost', user='scrapeuser', database='scraped_news', password=PASSWORD)
            cursor = connection.cursor()
            for command in commands:
                cursor.execute(command)
                connection.commit()
            cursor.close()
            connection.close()
            setupDB.insertSpiderRecords(PASSWORD, *SPIDER_DETAILS)
        except Exception as Error:
            print ("Error 102: ", Error)


    def insertSpiderRecords(PASSWORD, *SPIDER_DETAILS):
        try:
            connection = psycopg2.connect(host='localhost', user='scrapeuser', database='scraped_news', password=PASSWORD)
            cursor = connection.cursor()
            for command in SPIDER_DETAILS:
                try:
                    cursor.execute("""INSERT INTO site_table (id, site_name, site_url) VALUES (%s, %s, %s)""", (command['site_id'], command['site_name'], command['site_url']))
                except psycopg2.IntegrityError as Error:
                    print ("Error 104: ", Error)
                connection.commit()
            cursor.close()
            connection.close()
        except Exception as Error:
            print ("Error 103: ", Error)



if __name__ == '__main__':
    setupDB.createDatabase(PASSWORD)
