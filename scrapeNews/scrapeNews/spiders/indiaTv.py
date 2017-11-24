# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import logging
logger = logging.getLogger("scrapeNews")


class IndiatvSpider(scrapy.Spider):
    name = 'indiaTv'
    allowed_domains = ['www.indiatvnews.com']
    start_urls = ['http://www.indiatvnews.com']

    def parse(self, response):
        newsContainer = response.xpath('//div[@class="row latest_news"]/ul[@class="h_story normal"]/li')
        for newsBox in newsContainer:
            link = newsBox.xpath('a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.parse_article)

    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = self.getPageLink(response)
        item['source'] = 102
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item


    def getPageTitle(self, response):
        data = response.xpath('//h1[@class="arttitle"]/text()').extract_first()
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data

    def getPageLink(self, response):
        data = response.url
        if (data is None):
            logger.error(response)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath('//div[@class="content"]/div/figure/img/@src').extract_first()
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = response.xpath("//span[@class='dattime']/text()").extract()[1].rsplit(' ',3)[0]
        except (TypeError,IndexError) as Error:
            logger.error(response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = ' '.join((' '.join(response.xpath("//div[@class='content']/p/text()").extract())).split(' ')[:30])
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data
