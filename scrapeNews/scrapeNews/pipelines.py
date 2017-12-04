# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapeNews.items import ScrapenewsItem
from datetime import datetime
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
loggerInfo = logging.getLogger("scrapeNewsInfo")

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

    def open_spider(self, spider):
        try:
            self.connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database=os.environ['DATABASE_NAME'],
                password=os.environ['PASSWORD'])
            self.cursor = self.connection.cursor()
            self.connection.set_session(autocommit=True)
            commands = [
                "CREATE TABLE IF NOT EXISTS "+os.environ['SITE_TABLE']+" (id SMALLINT PRIMARY KEY, site_name VARCHAR NOT NULL, site_url VARCHAR NOT NULL)",
                "CREATE TABLE IF NOT EXISTS "+os.environ['NEWS_TABLE']+" (id SERIAL PRIMARY KEY, title VARCHAR NOT NULL, content VARCHAR NOT NULL, link VARCHAR NOT NULL UNIQUE, image VARCHAR NOT NULL, newsDate TIMESTAMP WITHOUT TIME ZONE NOT NULL, datescraped TIMESTAMP WITHOUT TIME ZONE, site_id SMALLINT NOT NULL REFERENCES site_table (id) ON DELETE CASCADE)"
            ]
            for command in commands:
                self.cursor.execute(command)
            try:
                self.cursor.execute("""INSERT INTO site_table (id, site_name, site_url) VALUES (%s, %s, %s)""",(
                    spider.custom_settings['site_id'],
                    spider.custom_settings['site_name'],
                    spider.custom_settings['site_url']))
            except psycopg2.IntegrityError as Error:
                pass
            self.recordedArticles = 0
        except Exception as Error:
            loggerError.error(Error)


    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.connection.close()
            if self.recordedArticles > 0:
                loggerInfo.info(str(self.recordedArticles) + " record(s) were added by " + spider.name + " at")
        except Exception as Error:
            loggerError.error(Error)


    def process_item(self, item, spider):
        try:
            postgresQuery = "SELECT link from " + os.environ['NEWS_TABLE'] + " where link= %s"
            self.cursor.execute(postgresQuery, (item.get('link'),))
            if not self.cursor.fetchall():
                processedDate = self.process_date(item.get('newsDate'),item.get('link'), spider.name)
                try:
                    postgresQuery = "INSERT INTO " + os.environ['NEWS_TABLE'] + " (title, content, image, link, newsDate, site_id, datescraped) VALUES (%s, %s, %s, %s, %s, %s, NOW())"
                    self.cursor.execute(postgresQuery,
                        (item.get('title'),
                        item.get('content'),
                        item.get('image'),
                        item.get('link'),
                        processedDate,
                        item.get('source')))
                    self.recordedArticles += 1
                except Exception as Error:
                    loggerError.error(str(Error) + " occured at " + str(item.get('link')))
                finally:
                    return item
            else:
                return item
        except Exception as Error:
            loggerError.error(str(Error) + " occured at " + str(item.get('link')))
            return item


    def process_date(self, itemDate, link, spiderName):
        try:
            if spiderName is 'indianExpressTech':
                processedItemDate = (datetime.strptime(itemDate,"%B %d, %Y %I:%M %p")).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'moneyControl':
                processedItemDate = (datetime.strptime(itemDate,"%B %d, %Y %I:%M %p %Z")).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'indiaTv':
                processedItemDate = (datetime.strptime(itemDate,"%B %d, %Y %H:%M")).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'zee':
                processedItemDate = (datetime.strptime(itemDate," %b %d, %Y, %H:%M %p")).strftime("%Y-%m-%dT%H:%M:%S")
            # elif spiderName is 'ndtv':
            #     processedItemDate = (datetime.strptime(itemDate, '%A %B %d, %Y')).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'asianage':
                processedItemDate = (datetime.strptime(itemDate,"%d %b %Y %I:%M %p")).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'News18Spider':
                processedItemDate = itemDate.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                processedItemDate = itemDate
        except ValueError as Error:
            loggerError.error(Error, link)
            processedItemDate = itemDate
        finally:
            return processedItemDate


class InnerSpiderPipeline(object):


    def openConnection(self):
        try:
            self.connection = psycopg2.connect(
                host= os.environ['HOST_NAME'],
                user=os.environ['USERNAME'],
                database=os.environ['DATABASE_NAME'],
                password=os.environ['PASSWORD'])
            self.connection.set_session(readonly=True, autocommit=True)
            self.cursor = self.connection.cursor()
        except Exception as Error:
            loggerError.error(Error)


    def closeConnection(self):
        self.cursor.close()
        self.connection.close()


    def checkUrlExists(self, item):
        postgresQuery = "SELECT link from " + os.environ['NEWS_TABLE'] + " where link= %s"
        try:
            self.cursor.execute(postgresQuery, (item,))
            if self.cursor.fetchall():
                return True
            else:
                return False
        except Exception as Error:
            loggerError.error(Error)
            return True
