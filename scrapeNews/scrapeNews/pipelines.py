# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapeNews.items import ScrapenewsItem
from datetime import datetime
import envConfig
import logging
loggerError = logging.getLogger("scrapeNewsError")
loggerInfo = logging.getLogger("scrapeNewsInfo")

# Setting up local variables USERNAME & PASSWORD
PASSWORD = envConfig.PASSWORD
USERNAME = envConfig.USERNAME


class ScrapenewsPipeline(object):

    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host='localhost',
            user=USERNAME,
            database='scraped_news',
            password=PASSWORD)
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True
        self.recordedArticles = 0

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
        if self.recordedArticles > 0:
            loggerInfo.info(str(self.recordedArticles) + " record(s) were added by " + spider.name + " at")

    def process_item(self, item, spider):
        self.cursor.execute("""SELECT link from news_table where link= %s """, (item.get('link'),))
        if not self.cursor.fetchall():
            processedDate = self.process_date(item.get('newsDate'),item.get('link'), spider.name)
            try:
                self.cursor.execute(
                    """INSERT INTO news_table (title, content, image, link, newsDate, site_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                    (item.get('title'),
                    item.get('content'),
                    item.get('image'),
                    item.get('link'),
                    processedDate,
                    item.get('source')))
                self.recordedArticles += 1
            except Exception as Error:
                loggerError.error(Error)
            finally:
                return item
        else:
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
                processedItemDate = (datetime.strptime(itemDate,"%b %d, %Y, %H:%M %p")).strftime("%Y-%m-%dT%H:%M:%S")
            elif spiderName is 'ndtv':
                processedItemDate = (datetime.strptime(itemDate, '%A %B %d, %Y')).strftime("%Y-%m-%dT%H:%M:%S")
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
