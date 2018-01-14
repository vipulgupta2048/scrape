# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger


class IndiatvSpider(scrapy.Spider):

    name = 'indiaTv'
    custom_settings = {
        'site_id':102,
        'site_name':'India TV',
        'site_url':'http://www.indiatvnews.com/india/'}


    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(IndiatvSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.indiatvnews.com/india/' + str(count + 1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' Non-200 response at ' + str(failure.request.url))

    def parse(self, response):
        try:
            newsContainer = response.xpath("//ul[@class='newsListfull']/li")
            for newsBox in newsContainer:
                link = newsBox.xpath('a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    self.urls_parsed += 1
                    yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)
                else
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] : " + str(e) + " : " + response.url)
        
    def parse_article(self, response):
        try:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 102
            if item['title'] is not 'Error' and item['content'] is not 'Error' and item['newsDate'] is not 'Error':
                self.urls_scraped += 1
                yield item
            else:
                self.urls_dropped += 1
                yield None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] : " + str(e) + " : " + response.url)
            self.urls_dropped += 1


    def getPageTitle(self, response):
        try:
            data = response.xpath('//h1[@class="arttitle"]/text()').extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Page Title: " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Page Title : " + str(e) + " : " + response.url)
            data = 'Error' 
        return data


    def getPageImage(self, response):
        try:
            data = response.xpath('//div[@class="content"]/div/figure/img/@src').extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Image : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(e) + " : " + response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = response.xpath("//span[@class='dattime']/text()").extract()[1].rsplit(' ', 3)[0]
        except Exception as Error:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Date : " + str(Error) + " : " + response.url)
            data = 'Error'
        return data


    def getPageContent(self, response):
        try:
            data = ' '.join(response.xpath("//div[@class='content']//*[not(self::script)]/text()").extract())
            if not data:
                logger.error(__name__ + " Unable to Extract Content : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Content : " + str(e) + " : "+ response.url)
            data = 'Error'
        return data
