# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from datetime import datetime

class nation(scrapy.Spider):
    name = "nnation"
    start_urls = ['http://www.newsnation.in/business-news',]
    #allowed_domains = ['http://www.newsnation.in/business-news']
    custom_settings = {
        'site_id':117,
        'site_name':'newsnation',
        'site_url':'http://www.newsnation.in/business-news'}
    
    #Scraping the main page for article links
    def parse(self,response):
        try:
            newsBox = response.xpath('//ul[contains(@class, "ciln")]/li')
            for box in newsBox:
                link = box.xpath('./div[2]/h2/a/@href').extract_first()
                self.urls_parsed += 1
                yield response.follow(link, callback = self.parse_article)

            #For scraping the links on the next page of the website
            next_page = response.xpath('//a[@rel="next"]/@href').extract_first()
            if next_page is not None:
                logger.info(__name__ + "=================Switching Page==================")
                yield response.follow(next_page, callback = self.parse)
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    #For scraping a particular article listed on the main page
    def parse_article(self,response):
        try:
            i = ScrapenewsItem()
            i['title'] = self.gettitle(response)
            i['link'] = self.getlink(response) #response.url 
            i['image'] = self.getimage(response)
            i['newsDate'] = self.getdatetime(response)
            i['content'] = self.getcontent(response)
            i['source'] = 117
            
            if i['title'] is not 'Error' and i['content'] is not 'Error' and i['link'] is not 'Error' and i['newsDate'] is not 'Error':
                    self.urls_scraped += 1
                    yield i
            else:
                self.urls_dropped += 1
                yield None
        except Exception as e:
            logger.error(__name__ + " [UNHNADLED] " + str(e) + " for response url " + response.url)
            yield None

    def gettitle(self,response):
        try:
            data = response.xpath("//h1/text()").extract_first() 
            if data is None:
                return 0
            if not data:
                logger.error(__name__ + " Unable to Extract Title " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Title : " + str(e) + " : " + response.url)
            data = 'Error'
        return data   

    def getdatetime(self,response):
        try:
            data = response.xpath('//span[contains(@itemprop, "date")]/text()').extract_first() 
            if data is None:
                return 0
            z = (datetime.strptime(data," %d %b , %Y , %H:%M %p")).strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as Error:
            logger.error(__name__+ " [UNHANDLED] Unable to Extract Date : " + str(Error) + " : " + response.url)
            data = 'Error'
        return data
            
    def getcontent(self,response):
        try:
            data = response.xpath('//div[@itemprop ="articleBody"]//p/text()').extract()
            if not data:
                data = response.xpath('//div[@itemprop ="articleBody"]//span/text()').extract()
            if not data or data is None:    
                logger.error(__name__ + " Unable to Extract Content : " response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data
        
    def getimage(self,response):
        try:
            data = response.xpath('//div[contains(@itemprop, "image")]//img/@src').extract_first()
            if data is None:
                return 0
            if not data:
                data = response.xpath("//meta[@property='og:image']/@content").extract_first()
            if not data:    
                logger.error(__name__ + " Unable to Extract Image : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(e) + " : " + response.url)
            data = 'Error'
        return data
        
    def getlink(self,response):
        try: 
            data = response.url
            if data == start_urls:
                logger.error(__name__+ " Unable to Extract Link : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Link : " + str(e) + " : " + response.url)
            data = 'Error'
        return data