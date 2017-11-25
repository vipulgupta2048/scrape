# Setting Up Database with imformation as given above
import psycopg2
import envConfig
import logging
loggerError = logging.getLogger("scrapeNewsError")

class setupDB:

    def createDatabase(USERNAME, PASSWORD):
        try:
            connection = psycopg2.connect(
                host='localhost',
                user=USERNAME,
                database='postgres',
                password=PASSWORD)
            cursor = connection.cursor()
            connection.autocommit = True
            cursor.execute('CREATE DATABASE scraped_news')
            cursor.close()
            connection.close()
            setupDB.createTables(USERNAME, PASSWORD)
        except psycopg2.ProgrammingError as Error:
            setupDB.createTables(USERNAME, PASSWORD)
        except Exception as Error:
            loggerError.error(Error)
    def createTables(USERNAME, PASSWORD):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS site_table (
                id SMALLINT PRIMARY KEY,
                site_name VARCHAR NOT NULL,
                site_url VARCHAR NOT NULL
                )
            """,
            """
            CREATE TABLE IF NOT EXISTS news_table (
                id SERIAL PRIMARY KEY,
                title VARCHAR NOT NULL,
                content VARCHAR NOT NULL,
                link VARCHAR NOT NULL,
                image VARCHAR NOT NULL,
                newsDate VARCHAR NOT NULL,
                site_id SMALLINT NOT NULL REFERENCES site_table (id)
            )
            """
        )
        try:
            connection = psycopg2.connect(
                host='localhost',
                user=USERNAME,
                database='scraped_news',
                password=PASSWORD)
            cursor = connection.cursor()
            for command in commands:
                cursor.execute(command)
                connection.commit()
            cursor.close()
            connection.close()
            setupDB.insertSpiderRecords(USERNAME, PASSWORD, *SPIDER_DETAILS)
        except Exception as Error:
            loggerError.error(Error)
    def insertSpiderRecords(USERNAME, PASSWORD, *SPIDER_DETAILS):
        try:
            connection = psycopg2.connect(
                host='localhost',
                user=USERNAME,
                database='scraped_news',
                password=PASSWORD)
            cursor = connection.cursor()
            for command in SPIDER_DETAILS:
                try:
                    cursor.execute(
                        """INSERT INTO site_table (id, site_name, site_url) VALUES (%s, %s, %s)""",
                        (command['site_id'],
                         command['site_name'],
                         command['site_url']))
                except psycopg2.IntegrityError as Error:
                    pass
                connection.commit()
            cursor.close()
            connection.close()
            print("\nDatabase setup successfully completed!\n")
        except Exception as Error:
            loggerError.error(Error)

if __name__ == '__main__':
    # Setting up local variables USERNAME, PASSWORD & SPIDER_DETAILS
    USERNAME = envConfig.USERNAME
    PASSWORD = envConfig.PASSWORD
    SPIDER_DETAILS = envConfig.SPIDER_DETAILS

    # Called to begin Database Setup
    setupDB.createDatabase(USERNAME, PASSWORD)
