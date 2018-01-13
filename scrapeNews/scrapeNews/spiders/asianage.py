# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger

class AsianageSpider(scrapy.Spider):

    name = 'asianage'
    allowed_domains = ['asianage.com']
    start_urls = ['http://asianage.com/']
    custom_settings = {
        'site_id':115,
        'site_name':'asianage',
        'site_url':'http://www.asianage.com/newsmakers'}

    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(AsianageSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.asianage.com/newsmakers?pg='+ str(count+1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' Non-200 response at ' + str(failure.request.url))

    def parse(self, response):
        try:
            newsContainer = response.xpath("//div[@class='singlesunday']")
            for newsBox in newsContainer:
                link = 'http://www.asianage.com' + newsBox.xpath('div/h2/a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    self.urls_parsed += 1
                    yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)
                else:
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def parse_article(self, response):
        try:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 115
            if item['title'] is not 'Error' and item['content'] is not 'Error' and item['newsDate'] is not 'Error':
                self.urls_scraped += 1
                yield item
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def getPageTitle(self, response):
        try:
            data = response.xpath("head/title/text()").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to extract page title " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract page title : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        try:
            data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to extract Image  " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Image : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first())
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Date : " + str(e) + " : " + response.url)
            data = 'Error'        
        return data

    def getPageContent(self, response):
        try:
            data = ' '.join(response.xpath("//div[@id='storyBody']/p/text()").extract())
            if not data:
                data = ' '.join(response.xpath("//div[@id='storyBody']/p//text()").extract())
            if not data:
                logger.error(__name__ + " Unable to extract page content " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data