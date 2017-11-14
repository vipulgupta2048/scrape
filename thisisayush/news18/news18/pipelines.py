# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from scrapy.exceptions import DropItem
from news18.db import NewsDatabase
from settings import logger
import re

class News18Pipeline(object):
    """Pipeline to check/create site """
    def open_spider(self, spider):
        logger.info(__name__+"[SPIDER_STARTED]"+spider.name)
        site_id = self.checkSite(spider)
        return {'site_id':site_id}
        
    def process_item(self, item, spider):
        return item

    def checkSite(self, spider):
        """ Check if website exists in database and fetch site id, else create new """
        #Connect To DATABASE
        database = NewsDatabase()
        con = database.connect()

        #Fetch Current Spider Details
        spider_name = spider.custom_settings['site_name']
        spider_url = spider.custom_settings['site_url']
        
        #Try to get SITE_ID from Database
        site_id = database.getSiteId(spider_name)
        
        if site_id == False:
            # SITE_ID == False, Add Site to Database
            try:
                logger.debug(__name__+" Site "+spider_name+" was Not Found! Creating Now!")

                con.execute(database.insert_site_str, (spider_name, spider_url))
                database.conn.commit()
                site_id = database.getSiteId(spider_name)
            
                #Save SITE_ID to Spider
                spider.custom_settings['site_id'] = site_id
            except Exception as e:
                logger.error(__name__+' [spider_name::spider_url] UNABLE TO ADD SITE TO DATABASE :: '+str(e))
                database.conn.rollback()
                return False
        else:
            # SITE Exists
            logger.info("Site "+spider_name+" exists in database with id "+ str(site_id))
            # Save SITE_ID to Spider
            spider.custom_settings['site_id'] = site_id
        database.conn.close()
        
        return site_id

class DuplicatesPipeline(object):
    """ Checks for Duplicate Links Missed by Spider """
    def open_spider(self, spider):
        site_id = spider.custom_settings['site_id']
        spider.custom_settings['urls_scraped'] = NewsDatabase().getUrlsScraped(site_id)

    def process_item(self, item, spider):
        # Choice 1 (List Method) 
        if item['url'] in spider.custom_settings['urls_scraped']:
            logger.info(__name__+"  [DROPPED] URL "+item['url']+" Already Scraped")
            raise DropItem("[DROPPED] URL "+item['url']+" Already Scraped")
        else:
            return item
        """
        # Choice 2 (DATABASE METHOD)
        if NewsDatabase().urlExists(item['url']):
            logger.debug(__name__+"  [DROPPED] URL "+item['url']+" Already Scraped")
            raise DropItem("[DROPPED] URL "+item['url']+" Already Scraped")
        else:
            return item
        """

class DataFilterPipeline(object):
    """Removes Unncessary Data from the item"""
    
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
        item['title'] = self.processRegex(item['title'])
        item['description'] = self.processRegex(item['description'])
        logger.debug(__name__+" Cleaned Item: "+str(item))
        return item
    
    def processRegex(self, text):
        for test in self.regex_match:
            text = re.sub(self.regex_match[test]['test'], self.regex_match[test]['replace'] , text)
        return text

class PostgresPipeline(object):
    """Adds Item to Database"""
    def process_item(self, item, spider):
        database = NewsDatabase()
        cur = database.connect()
        
        site_id = spider.custom_settings['site_id']
        logger.debug(__name__+" Received Item for SITE_ID "+str(site_id))

        try:
            cur.execute(database.insert_item_str, (item['title'], item['url'], item['description'], item['image'], site_id))
            database.conn.commit()
            logger.debug(__name__+" Added Item #"+str(cur.lastrowid)+" :: "+str(item))
            logger.info(__name__+" Finish Scraping "+item['url'])
            spider.custom_settings['urls_scraped'].append(item['url'])
        except Exception as e:
            logger.error(" Unable to ADD Item "+str(item)+" due to "+str(e))
            database.conn.rollback()
        return item
