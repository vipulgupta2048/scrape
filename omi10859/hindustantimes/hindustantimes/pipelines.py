# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from hindustantimes.database import Database

class HindustantimesPipeline(object):
    def process_item(self, item, spider):
        return item

#class Dropitem(object):

    #def process_item(self, item, spider):
        #print("look")
        #if len(item['link'])==0:
         #   return item 
        #else:
         #   print("Dropped")
          #  raise DropItem("no data %s" % item)

#class DuplicatePipelines(object):

    #def __init__(self):
     #   self.ids_seen = set()
    #def process_item(self, item, spider):
    #    if id 

class DatabasePipeline(object):

    def process_item(self, item, spider):
        print("Pipeline connected")
        database = Database()
        cur = database.connect()

        try:
            cur.execute(database.table_item, (item['title'], item['link'], item['newsDate'], item['content'], item['image']))
            print("working")
            database.conn.commit()
        
        except Exception as e:
            print("data does not added"+ str(e))
            database.conn.rollback()
        return item 
