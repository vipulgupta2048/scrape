# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from scrapy import signals
from scrapeNews.settings import DB_INFO, logger
from scrapeNews.db import postgresSQL, createDatabase
from scrapy.exceptions import CloseSpider, DropItem
from dateutil import parser

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
        """ Verifies if site exist in database, add otherwise """
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

    # Special Methods Below, Read about them before altering
    @classmethod
    def from_crawler(cls, crawler):
        temp = cls()
        crawler.signals.connect(temp.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(temp.item_dropped, signal=signals.item_dropped)
        return temp

    def spider_closed(self, spider, reason):
        # Calls After Spider is closed

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
        logger.info(__name__ + " [" + spider.name + "] SPIDER CLOSED")
    
    def item_dropped(self, item, response, exception, spider):
        # Calls When DropItem Exception is raised
        spider.urls_dropped += 1
        logger.info(__name__ + " [Dropped] <Spider>: " + spider.name + " <Reason>: " + str(exception) + " <Link>: " + str(item['link']))

class DuplicatesPipeline(object):
    """ Drops any accidentally sent Duplicate URLs """
    def process_item(self, item, spider):

        if not spider.postgres.checkConnection():
            raise CloseSpider("Unable to Establish a Database Connection")
        
        if spider.postgres.checkUrlExists(item['link']):
            raise DropItem("Url " + item['link'] + " Exists in Database")
        
        return item

class DataFormatterPipeline(object):
    """ Formats/Cleans Item Data to Specified Format """

    def process_item(self, item, spider):
        
        self.checkInvalidKeys(item)
        item['newsDate'] = self.process_date(item['newsDate'])
        
        return item

    def process_date(self, date):
        """ Processes Date and tries to convert it to Valid Python DateTime Object. Returns Formatted String """
        try:
            parsed_date = parser.parse(date, ignoretz=False, fuzzy=True)
            return str(parsed_date)
        except Exception as e:
            logger.error(__name__ + " Unable to Parse Date (Input: "+ str(date) + ") due to " + str(e))
            raise DropItem("Unable to Parse Date due to " + str(e))
    
    def checkInvalidKeys(self, item):
        """ Checks Keys For Invalid Entries Such as None/Empty """        
        allowedKeys = {
            'None': ["image"],
            'Empty': ["image"]
        }
        for key in item:
            try:
                if (item[key] == None or item[key] == "Error") and key not in allowedKeys['None']:
                    raise DropItem("Required Key " + str(key) + " is None")

                if(type(item[key]) is str and key not in allowedKeys['Empty']):
                    if len(item[key]) == 0:
                        raise DropItem("Required Key " + str(key) + " is Empty")
            except DropItem:
                pass
            except Exception as e:
                logger.error(__name__ + " Exception: " + str(e))
                continue

class DatabasePipeline(object):
    """ Communicates with Database and Stores Finalised Items """

    def process_item(self, item, spider):

        # Insert Item to Database
        if not spider.postgres.insertIntoNewsTable(item, spider.log_id):
            # If Error, Update Dropped Count
            spider.urls_dropped += 1
        else:
            # Update Stored Count
            spider.urls_stored += 1
        
        return item