# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from time import sleep


class MoneycontrolSpider(scrapy.Spider):

    name = 'moneyControl'
    allowed_domains = ['moneycontrol.com']
    custom_settings = {
        'site_id':108,
        'site_name':'moneyControl',
        'site_url':'http://www.moneycontrol.com/news/business/'}

    def __init__(self, pages=10, *args, **kwargs):
        super(MoneycontrolSpider, self).__init__(*args, **kwargs)
        for count in range(1 , int(pages)+1):
            self.start_urls.append('http://www.moneycontrol.com/news/business/page-'+ str(count))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)
            sleep(2)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' NON-200 response at ' + str(failure.request.url))


    def parse(self, response):
        try:
            newsContainer = response.xpath("//ul[@id='cagetory']/li[@class='clearfix']")
            for newsBox in newsContainer:
                link = newsBox.xpath('a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    self.urls_parsed += 1
                    yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)
                else:
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__+ " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def parse_article(self, response):
        try:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 108
            if item['title'] is not 'Error' and item['content'] is not 'Error' and item['newsDate'] is not 'Error':
                self.urls_scraped += 1
                yield item
            else:
                self.urls_dropped += 1
                yield None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url "+ response.url)
            self.urls_dropped += 1

    def getPageTitle(self, response):
        try:
            data = response.xpath("/html/head/meta[@property='og:title']/@content").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Page Title : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANLDED] Unable to Extract Page Title : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        try:
            data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Image : s" + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = response.xpath("/html/head/meta[@name='Last-Modified']/@content").extract_first()
        except Exception as Error:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Date : " + str(Error) + " : " + response.url)
            data = 'Error'
        return data

    def getPageContent(self, response):
        try:
            data = ' '.join(response.xpath("//div[@id='article-main']/p/text()").extract())
            if not data:
                data = ' '.join(response.xpath("//div[@itemprop='articleBody']/p/text()").extract())
            if not data:
                data = ' '.join(response.xpath("//meta[@property='og:description']/@content").extract())
            if not data:
                logger.error(__name__ + " Unable to Extract Content : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data
