# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import initialization
import psycopg2
from scrapeNews.items import ScrapenewsItem
from datetime import datetime
import logging
import os

loggerError = logging.getLogger("scrapeNewsError")
loggerInfo = logging.getLogger("scrapeNewsInfo")
postgresSQL = initialization.setupDatabase()
postgresSQL.createDatabase()


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
