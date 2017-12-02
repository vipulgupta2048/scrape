import psycopg2
import envConfig
import json
import os
import logging
loggerError = logging.getLogger("scrapeNewsError")

# Setting up environment variables
os.environ['USERNAME'] = envConfig.USERNAME
os.environ['PASSWORD'] = envConfig.PASSWORD
os.environ['SPIDER_DETAILS'] = str(envConfig.SPIDER_DETAILS)
os.environ['NEWS_TABLE'] = envConfig.NEWS_TABLE
os.environ['SITE_TABLE'] = envConfig.SITE_TABLE
os.environ['LOG_TABLE'] = envConfig.LOG_TABLE
os.environ['DATABASE_NAME'] = envConfig.DATABASE_NAME
os.environ['HOST_NAME'] = envConfig.HOST_NAME

class setupDatabase:

    def createDatabase(self):
        try:
            connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database='postgres',
                password=os.environ['PASSWORD'])
            cursor = connection.cursor()
            connection.autocommit = True
            postgresCommand = 'CREATE DATABASE ' + os.environ['DATABASE_NAME']
            cursor.execute(postgresCommand)
            cursor.close()
            connection.close()
            self.createTables()
        except psycopg2.ProgrammingError as Error:
            self.createTables()
        except Exception as Error:
            loggerError.error(Error)
    def createTables(self):
        commands = [
            "CREATE TABLE IF NOT EXISTS "+os.environ['SITE_TABLE']+" (id SMALLINT PRIMARY KEY, site_name VARCHAR NOT NULL, site_url VARCHAR NOT NULL)",
            "CREATE TABLE IF NOT EXISTS "+os.environ['NEWS_TABLE']+" (id SERIAL PRIMARY KEY, title VARCHAR NOT NULL, content VARCHAR NOT NULL, link VARCHAR NOT NULL UNIQUE, image VARCHAR NOT NULL, newsDate TIMESTAMP WITHOUT TIME ZONE NOT NULL, datescraped TIMESTAMP WITHOUT TIME ZONE, site_id SMALLINT NOT NULL REFERENCES site_table (id) ON DELETE CASCADE)"
        ]
        try:
            connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database=os.environ['DATABASE_NAME'],
                password=os.environ['PASSWORD'])
            cursor = connection.cursor()
            for command in commands:
                cursor.execute(command)
                connection.commit()
            cursor.close()
            connection.close()
            self.insertSpiderRecords()
        except Exception as Error:
            loggerError.error(Error)
    def insertSpiderRecords(self):
        SPIDER_DETAILS = json.loads(os.environ['SPIDER_DETAILS'].replace("'",'"')) # Replace used to make the string into a valid JSON.
        try:
            connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database=os.environ['DATABASE_NAME'],
                password=os.environ['PASSWORD'])
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
        except Exception as Error:
            loggerError.error(Error)

if __name__ == '__main__':
    # Called to begin Database Setup
    postgresSQL = setupDatabase()
    postgresSQL.createDatabase()
