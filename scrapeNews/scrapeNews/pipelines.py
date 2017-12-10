# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
import os
import re
import logging
from scrapeNews.items import ScrapenewsItem
from dateutil import parser
from .settings import logger, DbDateFormat
from scrapy.exceptions import DropItem, CloseSpider
from .db import DatabaseManager, LogsManager, ConnectionManager
#Calling logging module instance
loggerError = logging.getLogger("scrapeNewsError")
loggerInfo = logging.getLogger("scrapeNewsInfo")

class ScrapenewsPipeline(object):
    """
    This Pipeline Does Initial Spider Tasks,
    - Fetch/Assign SiteId to Spider on Start
    - Log Stats On Spider Close
    """
    def open_spider(self, spider):
        logger.info(__name__+" [Spider Started]: "+spider.name)
        spider.dbconn = DatabaseManager()
        if spider.dbconn.conn == None:
            raise CloseSpider("Unable to Establish a Database Connection!")
        site_id = self.checkSite(spider)
        spider.custom_settings['site_id'] = site_id
        spider.custom_settings['log_id'] = LogsManager().start_log(site_id)

    def checkSite(self, spider):
        """ Check if website exists in database and fetch site id, else create new """
        #Connect To DATABASE
        if not ConnectionManager(spider.dbconn).checkConnection():
            raise CloseSpider("Unable to Establish a Database Connection")
        database = spider.dbconn

        #Fetch Current Spider Details
        spider_name = spider.custom_settings['site_name']
        spider_url = spider.custom_settings['site_url']

        #Try to get SITE_ID from Database
        site_id = database.getSiteId(spider_name)

        if site_id == False:
            # SITE_ID == False, Add Site to Database
            try:
                logger.debug(__name__+" Site "+spider_name+" was Not Found! Creating Now!")
                if database.connect() != None:
                    database.cursor.execute(database.insert_site_str, (spider_name, spider_url))
                    database.conn.commit()
                    site_id = database.cursor.fetchone()['id']
                    #Save SITE_ID to Spider
                    spider.custom_settings['site_id'] = site_id
                else:
                    logger.error(__name__+' ['+spider_name+'::'+spider_url+'] Database Connection Failed ')

            except Exception as e:
                logger.error(__name__+' ['+spider_name+'::'+spider_url+'] Unable to add site :: '+str(e))
                database.conn.rollback()
        else:
            # SITE Exists
            logger.info("Site "+spider_name+" exists in database with id "+ str(site_id))
            # Save SITE_ID to Spider
            spider.custom_settings['site_id'] = site_id

        if site_id == False:
            # Send Spider Send Signal here
            raise CloseSpider("Unable to Assign SiteId to Spider "+spider.name)

        return site_id


    def close_spider(self, spider):
        #loggerInfo.info(str(self.recordedArticles) + " record(s) were added by " + spider.name + " at")
        spider.dbconn.conn.commit()
        spider.dbconn.conn.close()
        logger.info(__name__ + spider.name +"SPIDER CLOSED")

class DuplicatesPipeline(object):
    """
    This Pipeline Drops any Duplicate URL Missed by Spiders
    Please Use DatabaseManager().urlExists(url) in your spiders to preserve bandwidth and speed up process
    """
    def process_item(self, item, spider):
        if not ConnectionManager(spider.dbconn).checkConnection():
            raise CloseSpider("Unable to Establish a Database Connection")

        if spider.dbconn.urlExists(item['link']):
            logger.info(__name__+" [Dropped URL] "+item['link']+" Url Already in Database")
            spider.custom_settings['url_stats']['dropped'] += 1
            raise DropItem("[Dropped URL] "+item['link']+" Url Already in Database")
        else:
            return item

class DataFormatterPipeline(object):
    """
    This Pipeline Formats The Data for Database
    - Convert Date into specified common format
    - Removes Unncessary Data from the item
    """

    regex_match = {
        "line_end": {
            'test':r'\n',
            'replace':''
            },
        "multi_space": {
            'test':r'\s{2,}',
            'replace':' '
            },
        "white_space_beg_end": {
            'test':r"^\s{0,}|\s{0,}$",
            'replace': ''
                }
    }

    def process_item(self, item, spider):

        for x in item:
            if item[x] == None:
                logger.error(__name__ + " [" + spider.name + "] [DROPPED] " + x + " is None ")
                raise DropItem("Content Missing from Item")
            if len(item[x]) == 0:
                logger.error(__name__ + " [" + spider.name + "] [DROPPED] " + x + " is Empty")
                raise DropItem("Content Missing from Item")

        # Format Date
        item['newsDate'] = self.processDate(item['newsDate'], spider)

        # Format Data
        item['title'] = self.processRegex(item['title'])
        item['content'] = self.processRegex(item['content'])

        return item

    def processDate(self, dateStr, spider):
        try:
            date_parsed = parser.parse(dateStr, ignoretz=False, fuzzy=True)
            return date_parsed.strftime(DbDateFormat)
        except ValueError as e:
            logger.error(__name__ + " [" + spider.name + "] [DROPPED] Error Parsing Date: "+str(e))
            spider.custom_settings['url_stats']['dropped'] += 1
            raise DropItem("[ITEM DROPPED] "+str(e))

    def processRegex(self, text):
        for test in self.regex_match:
            text = re.sub(self.regex_match[test]['test'], self.regex_match[test]['replace'], text)
        return text

class DatabasePipeline(object):
    """
    This Pipeline Manages and Stores Processed Data into Database
    """
    def process_item(self, item, spider):
        if not ConnectionManager(spider.dbconn).checkConnection():
            raise CloseSpider("Unable to Establish a Database Connection")

        database = spider.dbconn
        cur = database.cursor

        site_id = spider.custom_settings['site_id']
        logger.debug(__name__+" Received Item for SITE_ID: "+str(site_id)) 

        try:
            cur.execute(database.insert_item_str, (item['title'], item['link'], item['content'], item['image'], item['newsDate'], site_id))
            database.conn.commit()
            logger.info(__name__+" Finish Scraping "+str(item['link']))
            spider.custom_settings['url_stats']['stored'] += 1
        except Exception as e:
            logger.error(__name__ + " [" + spider.name + "] Database Insertion Failed  due to " + str(e))
            spider.custom_settings['url_stats']['dropped'] += 1
            database.conn.rollback()
        LogsManager(database).update_log(spider.custom_settings['log_id'], spider.custom_settings['url_stats'])
        return item
