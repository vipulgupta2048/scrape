# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import LogsManager, DatabaseManager

class MoneycontrolSpider(scrapy.Spider):

    name = 'moneyControl'
    allowed_domains = ['moneycontrol.com']

    custom_settings = {
        'site_name': "moneyControl",
        'site_url': "http://www.moneycontrol.com/news/business/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "http://www.moneycontrol.com/news/business/page-"

    def start_requests(self):
        yield scrapy.Request(self.start_url+"1", self.parse)

    def parse(self, response):
        item = ScrapenewsItem()  # Scraper Items
        newsContainer = response.xpath("//ul[@id='cagetory']/li[@class='clearfix']")
        for newsBox in newsContainer:
            item = ScrapenewsItem()  # Scraper Items
            self.custom_settings['url_stats']['parsed'] += 1
            item['image'] = self.getPageImage(newsBox)
            item['title'] = self.getPageTitle(newsBox)
            item['content'] = self.getPageContent(newsBox)
            item['newsDate'] = self.getPageDate(newsBox)
            item['link'] = self.getPageLink(newsBox)

            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                if not DatabaseManager().urlExists(item['link']):
                    self.custom_settings['url_stats']['scraped'] += 1
                    yield item
                else:
                    self.custom_settings['url_stats']['dropped'] += 1
                    yield None
            else:
                self.custom_settings['url_stats']['dropped'] += 1
                yield None
        pagenation = response.xpath("//div[@class='pagenation']/a/@data-page").extract()
        next_page = response.urljoin(self.start_url+pagenation[-2])
        last_page = response.urljoin(self.start_url+pagenation[-1])

        if response.url != last_page:
            yield scrapy.Request(next_page, self.parse)


    def getPageContent(self, newsBox):
        data = newsBox.xpath('p/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Content: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageTitle(self, newsBox):
        data = newsBox.xpath('h2/a/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Title: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = newsBox.xpath('a/@href').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Link: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath('a/img/@src').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Image: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        data = newsBox.xpath('span/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Date: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with stats " + str(self.custom_settings['url_stats']))
