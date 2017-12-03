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
from scrapeNews.settings import logger, DbDateFormat
from scrapy.exceptions import DropItem, CloseSpider
from scrapeNews.db import DatabaseManager, LogsManager

class ScrapenewsPipeline(object):
    """
    This Pipeline Does Initial Spider Tasks,
    - Fetch/Assign SiteId to Spider on Start
    - Log Stats On Spider Close
    """
    def open_spider(self, spider):
        logger.info(__name__+" [Spider Started]: "+spider.name)
        site_id = self.checkSite(spider)
        spider.custom_settings['site_id'] = site_id
        spider.custom_settings['log_id'] = LogsManager().start_log(site_id)

    def checkSite(self, spider):
        """ Check if website exists in database and fetch site id, else create new """
        #Connect To DATABASE
        database = DatabaseManager()

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
                    site_id = con.fetchone()['id']
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
        logger.info(__name__ + spider.name +"SPIDER CLOSED")

class DuplicatesPipeline(object):
    """
    This Pipeline Drops any Duplicate URL Missed by Spiders
    Please Use DatabaseManager().urlExists(url) in your spiders to preserve bandwidth and speed up process
    """
    def process_item(self, item, spider):

        if DatabaseManager().urlExists(item['url']):
            logger.info(__name__+" [Dropped URL] "+item['url']+" Url Already in Database")
            spider.custom_settings['url_stats']['dropped'] += 1
            raise DropItem("[Dropped URL] "+item['url']+" Url Already in Database")
        else:
            return Item

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
        # Format Date
        item['date'] = processDate(item['date'])

        # Format Data
        item['title'] = self.processRegex(item['title'])
        item['content'] = self.processRegex(item['content'])
        
        return item

    def processDate(self, dateStr):
        date_parsed = parser.parse(dateStr, ignoretz=False)
        return date_parsed.strftime(DbDateFormat)

    def processRegex(self, text):
        for test in self.regex_match:
            text = re.sub(self.regex_match[test]['test'], self.regex_match[test]['replace'], text)
        return text

class DatabasePipeline(object):
    """
    This Pipeline Manages and Stores Processed Data into Database
    """
    def process_item(self, item, spider):
        database = DatabaseManager()
        cur = database.cursor

        site_id = spider.custom_settings['site_id']
        logger.debug(__name__+" Received Item for SITE_ID: "+str(site_id)) 

        try:
            cur.execute(database.insert_item_str, (item['title'], item['link'], item['content'], item['image'], item['date'], site_id))
            database.conn.commit()
            logger.info(__name__+" Finish Scraping "+str(item['link']))
            spider.custom_settings['url_stats']['stored'] += 1
        except Exception as e:
            logger.error(__name__+" Unable to Add Item "+str(item)+" due to "+str(e))
            database.conn.rollback()

        return item

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


    def checkUrlExists(self, link):
        self.spider.urls_parsed += 1
        # Check if the url already exists in the database.
        postgresQuery = "SELECT link from " + os.environ['NEWS_TABLE'] + " where link= %s"
        try:
            if (self.connection.status != 1):
                self.openConnection(self.spider)
            self.cursor.execute(postgresQuery, (link,))
            if self.cursor.fetchall():
                self.spider.urls_dropped += 1
                return True
            else:
                return False
        except Exception as Error:
            loggerError.error(Error)
            return True
