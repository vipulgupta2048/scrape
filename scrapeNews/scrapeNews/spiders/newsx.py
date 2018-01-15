# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from time import sleep


class NewsxSpider(scrapy.Spider):

    name = 'newsx'
    allowed_domains = ['newsx.com']
    start_urls = ['http://newsx.com/']
    custom_settings = {
        'site_id':113,
        'site_name':'newsx',
        'site_url':'http://www.newsx.com/latest-news/'}

    def __init__(self, offset=0, pages=4, *args, **kwargs):
        super(NewsxSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.newsx.com/latest-news/page/'+ str(count+1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)
            sleep(1)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        try:
            newsContainer = response.xpath("//div[contains(@class,'cat-grid-gap')]/div[@class='well ft2']")
            for newsBox in newsContainer:
                link = newsBox.xpath('div/a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    self.urls_parsed += 1
                    yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)
                    sleep(2)
                else:
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)


    def parse_article(self, response):
        try:
            if (response.url == 'http://www.newsx.com'):
                pass
            else:
                item = ScrapenewsItem()  # Scraper Items
                item['image'] = self.getPageImage(response)
                item['title'] = self.getPageTitle(response)
                item['content'] = self.getPageContent(response)
                item['newsDate'] = self.getPageDate(response)
                item['link'] = response.url
                item['source'] = 113
                if item['title'] is not 'Error' and item['content'] is not 'Error' and item['link'] is not 'Error' and item['newsDate'] is not 'Error':
                    self.urls_scraped += 1
                    yield item
                else:
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)


    def getPageTitle(self, response):
        try:
            data = ' '.join(response.xpath("//h1[@itemprop='headline']/text()").extract_first().split())
        except Exception as Error:
            logger.error(__name__  + " [UNHANDLED] Unable to Extract Title : " + str(Error) + " : "+ response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        try:
            data = response.xpath("//head/link[@rel='image_src']/@href").extract_first()
            if (data is None):
                data = response.xpath("//div[@class='panel-body story']/div[@class='thumbnail video-thumbnail']/img/@src").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Image : " +  response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@itemprop='datePublished']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Date : " + str(Error) + " : " + response.url)
            data = 'Error'
        return data

    def getPageContent(self, response):
        try:
            data = ' '.join(response.xpath("//div[@class='story-short-title']/h2/text()").extract())
            if not data:
                data = ' '.join(response.xpath("//div[@itemprop='articleBody']/p//text()").extract())
            if not data:
                data = ' '.join(response.xpath("//div[@itemprop='articleBody']/div//text()").extract())
            if not data:
                logger.error(__name__ + " Unable to Extract Content : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data