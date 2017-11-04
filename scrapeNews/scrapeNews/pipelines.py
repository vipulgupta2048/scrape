# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapeNews.items import ScrapenewsItem

class ScrapenewsPipeline(object):

    def open_spider(self, spider):
        self.connection = psycopg2.connect(host='localhost', user='scrapeuser', database='scraped_news', password='simple')
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
    def process_item(self, item, spider):
        try:
            self.cursor.execute("""INSERT INTO news_table (title, content, image, link, newsDate, site_id) VALUES (%s, %s, %s, %s, %s, %s)""" , (item.get('title'), item.get('content'), item.get('image'), item.get('link'), item.get('newsDate'), item.get('source')))
            self.connection.commit()
        except Exception as Error:
            print ("Error 103: ", Error)
        finally:
            return item
