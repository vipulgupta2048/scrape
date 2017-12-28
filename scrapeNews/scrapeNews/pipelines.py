# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os
from scrapy import signals
from scrapeNews.settings import DB_INFO, logger
from scrapeNews.db import postgresSQL, createDatabase
from scrapy.exceptions import CloseSpider

# Setting Environment Variables

os.environ['USERNAME'] = DB_INFO['USERNAME']
os.environ['PASSWORD'] = DB_INFO['PASSWORD']
os.environ['NEWS_TABLE'] = DB_INFO['NEWS_TABLE']
os.environ['SITE_TABLE'] = DB_INFO['SITE_TABLE']
os.environ['LOG_TABLE'] = DB_INFO['LOG_TABLE']
os.environ['DATABASE_NAME'] = DB_INFO['DATABASE_NAME']
os.environ['HOST_NAME'] = DB_INFO['HOST_NAME']

# Calling logging module instance
loggerError = logging.getLogger("scrapeNewsError")

#Calling to create database if it doesn't exist already!
createDatabase()

class ScrapenewsPipeline(object):
    # This class serves the purpose of cleaning the items received from spider,
    # Calling the instance of spider's postgresSQL class and calling functions
    # to create and destroy connection as and when needed.

    def open_spider(self, spider):
        # Called when a spider starts

        #Create a dedicated Database Connection for the spider
        spider.postgres = postgresSQL()

        #Verify the Connection
        if spider.postgres.connect() == False:
            raise CloseSpider(" Database Connection cannot be established!")

        #Initialize the Stats
        spider.urls_dropped = 0
        spider.urls_scraped = 0
        spider.urls_parsed = 0
        spider.urls_stored = 0

        #Add/Verify Site in Database
        self.checkSite(spider)

        #Start Spider's Log
        spider.log_id = spider.postgres.start_log(spider.custom_settings['site_id'], os.getpid())
        if not spider.log_id:
            raise CloseSpider(" Unable to Start Log!")

    def checkSite(self, spider):
        # Verify Database Connection
        if not spider.postgres.checkConnection():
            logger.error(__name__ + " No Database Connection Found!")
            raise CloseSpider(" No Database Connection Found!")
        
        try:
            # Check if site Exists in Database using it's site_id
            if not spider.postgres.siteExists(spider.custom_settings['site_id']):
                # Add it to Database if not
                spider.postgres.cursor.execute(spider.postgres.insert_site_str, (
                    spider.custom_settings['site_id'],
                    spider.custom_settings['site_name'],
                    spider.custom_settings['site_url'],
                    spider.name,
                    )
                )
        except Exception as e:
            logger.error(__name__ + " Unable to add site to Database! Msg: " + str(e))
            raise CloseSpider("Unable to add site to Database")

    def process_item(self, item, spider):

        # Insert Item to Database
        if not spider.postgres.insertIntoNewsTable(item, spider.log_id):
            # If Error, Update Dropped Count
            spider.urls_dropped += 1
        else:
            # Update Stored Count
            spider.urls_stored += 1
        
        return item
    
    # Special Methods Below, Read about them before altering
    @classmethod
    def from_crawler(cls, crawler):
        temp = cls()
        crawler.signals.connect(temp.spider_closed, signal=signals.spider_closed)
        return temp

    def spider_closed(self, spider, reason):
        # Check Connection
        if not spider.postgres.checkConnection():
            raise CloseSpider("Unable to Establish a Database Connection")

        # Collect all Stats
        url_stats = {
            "urls_dropped": spider.urls_dropped,
            "urls_scraped": spider.urls_scraped,
            "urls_parsed": spider.urls_parsed,
            "urls_stored": spider.urls_stored
        }

        # End The Log
        if not spider.postgres.end_log(spider.log_id, url_stats, reason):
            logger.error(__name__ + " Unable to End Log for Spider " + spider.name + " with stats: " + str(url_stats))
        
        # Close the database connection
        spider.postgres.connection.close()
        logger.info(__name__ + spider.name +" SPIDER CLOSED")