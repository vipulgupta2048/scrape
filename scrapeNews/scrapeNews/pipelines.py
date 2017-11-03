# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapeNews.items import ScrapenewsItem

class ScrapenewsPipeline(object):
    def __init__(self):
        self.connection = psycopg2.connect(host='localhost', database='scrapeNews', user='postgres')
        self.cursor = self.connection.cursor()


    def process_item(self, item, spider):
        try:
            self.cursor.execute("""INSERT INTO news (title, content, image, link, newsDate) VALUES(%s, %s, %s, %s, %s, %s, %s)""", (item.get('title'), item.get('content'), item.get('image'), item.get('link'), item.get('newsDate'),))
            self.connection.commit()
            self.cursor.fetchall()
        except psycopg2.DatabaseError, Error:
            print ("Error: ",Error)
        finally:
            return item
