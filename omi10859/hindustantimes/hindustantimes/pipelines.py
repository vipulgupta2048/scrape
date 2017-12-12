# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2 
from scrapy.exceptions import DropItem
from hindustantimes.database import Database

class HindustantimesPipeline(object):
    def process_item(self, item, spider):
        return item

class Dropitem(object):

    def process_item(self, item, spider):
        variable = item['link']
        if variable:
            print("not dropping")
            return item 
        else:
            print("Dropped")
            raise DropItem("no data %s" % item['link'])

class DuplicatePipelines(object):

    def process_item(self, item, spider):
        try:
            if Database().url(item['link']):
                print("data alredy in table")
                raise DropItem("[DROPPED] URL "+item['url']+" Already Scraped")
            else:
                return item
        except:
            return item         

class DatabasePipeline(object):

    def process_item(self, item, spider):
        print("Pipeline connected")
        database = Database()
        cur = database.connect()

        try:
            cur.execute(database.table_item, (item['title'], item['link'], item['date'], item['content'], item['image']))
            print("working")
            database.conn.commit()
        
        except Exception as e:
            print("data does not added"+ str(e))
            database.conn.rollback()
        return item 