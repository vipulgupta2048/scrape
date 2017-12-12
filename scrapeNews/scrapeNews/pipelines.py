# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapeNews.items import ScrapenewsItem
from dateutil import parser
import logging
import envConfig
import os

# Setting up environment variables
os.environ['USERNAME'] = envConfig.USERNAME
os.environ['PASSWORD'] = envConfig.PASSWORD
os.environ['NEWS_TABLE'] = envConfig.NEWS_TABLE
os.environ['SITE_TABLE'] = envConfig.SITE_TABLE
os.environ['LOG_TABLE'] = envConfig.LOG_TABLE
os.environ['DATABASE_NAME'] = envConfig.DATABASE_NAME
os.environ['HOST_NAME'] = envConfig.HOST_NAME

# Calling logging module instance
loggerError = logging.getLogger("scrapeNewsError")

def createDatabase():
    # This function is creating the database, it is different that others because it uses a
    # different connection (because you cannot create a database while on it, duh!)
    # It can be called anytime to create the database and is called automatically when scrapy crawls
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
    except psycopg2.ProgrammingError as Error:
        pass
    except Exception as Error:
        loggerError.error(Error)

# Calling to create database if it doesn't exist already!
createDatabase()


class ScrapenewsPipeline(object):
    # This class serves the purpose of cleaning the items received from spider,
    # Calling the instance of spider's postgresSQL class and calling functions
    # to create and destroy connection as and when needed.

    def open_spider(self, spider):
        # Called when a spider starts
        spider.postgres = postgresSQL()
        spider.postgres.openConnection(spider)

    def close_spider(self, spider):
        # Called when a spider closes it can't be used with logging enabled
        # because it is called just before the spider is closed and logging
        # table needs close reason, generated at close
        pass

    def process_item(self, item, spider):
        spider.postgres.insertIntoNewsTable(item)


class postgresSQL(object):
    # postgresSQL class will be the class that has connection when the with postgresSQL
    # and all database related operations must take place here, (In favour of keeping the
    # number of connections low )
    def openConnection(self, spider):
        # Makes a connection with postgresSQL using pyscopg2
        self.spider = spider
        try:
            self.connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database=os.environ['DATABASE_NAME'],
                password=os.environ['PASSWORD'])
            self.cursor = self.connection.cursor()
            self.connection.set_session(autocommit=True)
            commands = [
                "CREATE TABLE IF NOT EXISTS "+os.environ['SITE_TABLE']+" (id SMALLINT PRIMARY KEY, site_name VARCHAR NOT NULL, site_url VARCHAR NOT NULL, status_check TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW())",
                "CREATE TABLE IF NOT EXISTS "+os.environ['NEWS_TABLE']+" (id SERIAL PRIMARY KEY, title VARCHAR NOT NULL, content VARCHAR NOT NULL, link VARCHAR NOT NULL UNIQUE, image VARCHAR NOT NULL, newsDate TIMESTAMP WITHOUT TIME ZONE NOT NULL, datescraped TIMESTAMP WITHOUT TIME ZONE, site_id SMALLINT NOT NULL REFERENCES site_table (id) ON DELETE CASCADE)",
                "CREATE TABLE IF NOT EXISTS "+os.environ['LOG_TABLE']+" (id SERIAL PRIMARY KEY, spider_id SMALLINT REFERENCES site_table (id) ON DELETE CASCADE, process_id SMALLINT NOT NULL, start_time TIMESTAMP WITHOUT TIME ZONE, end_time TIMESTAMP WITHOUT TIME ZONE, urls_parsed SMALLINT, urls_scraped SMALLINT, urls_dropped SMALLINT, urls_stored SMALLINT, close_reason VARCHAR)"
            ]
            for command in commands:
                self.cursor.execute(command)
            try:
                command = "INSERT INTO "+os.environ['SITE_TABLE']+" (id, site_name, site_url) VALUES (%s, %s, %s)"
                self.cursor.execute(command,(
                    self.spider.custom_settings['site_id'],
                    self.spider.custom_settings['site_name'],
                    self.spider.custom_settings['site_url']))
            except psycopg2.IntegrityError as Error:
                pass
            # Initializing values as 0 for log information
            self.spider.urls_dropped = 0
            self.spider.urls_scraped = 0
            self.spider.urls_parsed = 0
            self.spider.urls_stored = 0
            self.spider.start_time =  str(parser.datetime.datetime.now())
            command = "INSERT INTO "+os.environ['LOG_TABLE']+" (spider_id, process_id, start_time, close_reason) VALUES (%s, %s, %s, 'crawling')"
            self.cursor.execute(command,(
                spider.custom_settings['site_id'],
                os.getpid(),
                spider.start_time))
        except Exception as Error:
            loggerError.error(Error)


    def closeConnection(self,reason):
        # closes connection with postgreSQL using pyscopg2
        try:
            command = "UPDATE "+os.environ['LOG_TABLE']+" SET end_time=NOW(), urls_dropped=%s, urls_scraped=%s, urls_parsed=%s, urls_stored=%s, close_reason=%s WHERE spider_id=%s AND process_id=%s AND start_time=%s"
            self.cursor.execute(command,(
                self.spider.urls_dropped,
                self.spider.urls_scraped,
                self.spider.urls_parsed,
                self.spider.urls_stored,
                reason,
                self.spider.custom_settings['site_id'],
                os.getpid(),
                self.spider.start_time))
            self.cursor.close()
            self.connection.close()
            if self.spider.urls_stored > 0:
                print (str(self.spider.urls_stored) + " record(s) were added by " + self.spider.name + " at " + parser.datetime.datetime.strftime(parser.datetime.datetime.now(),'%I:%M:%S'))
        except Exception as Error:
            loggerError.error(Error)


    def insertIntoNewsTable(self, item):
        # Insert item into NEWS_TABLE after all the processing.
        try:
            if (self.connection.status != 1):
                self.openConnection(self.spider)
            postgresQuery = "INSERT INTO " + os.environ['NEWS_TABLE'] + " (title, content, image, link, newsDate, site_id, datescraped) VALUES (%s, %s, %s, %s, %s, %s, NOW())"
            processedDate = str(parser.parse(item.get('newsDate'), ignoretz=False))
            self.cursor.execute(postgresQuery,
                (item.get('title'),
                item.get('content'),
                item.get('image'),
                item.get('link'),
                processedDate,
                item.get('source')))
            self.spider.urls_stored += 1
        except psycopg2.IntegrityError as Error:
            # If the link already exists, this exception will be invoked
            if (Error.pgcode == '23505'):
                pass
            else:
                loggerError.error(str(Error) + " occured at " + str(item.get('link')))
        except Exception as Error:
            loggerError.error(str(Error) + " occured at " + str(item.get('link')))
        finally:
            return item


    def checkUrlExists(self, link):
        self.spider.urls_parsed += 1
        # Check if the url already exists in the database.
        postgresQuery = "SELECT link from " + os.environ['NEWS_TABLE'] + " where link= %s"
        try:
            if (self.connection.status != 1):
                self.openConnection(self.spider)
            self.cursor.execute(postgresQuery, (link,))
            if self.cursor.fetchall():
                self.spider.urls_dropped += 1
                return True
            else:
                return False
        except Exception as Error:
            loggerError.error(Error)
            return True
