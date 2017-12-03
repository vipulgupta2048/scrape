# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from scrapeNews.db import LogsManager

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


    def __init__(self, pages=10, *args, **kwargs):
        super(MoneycontrolSpider, self).__init__(*args, **kwargs)
        for count in range(1 , int(pages)+1):
            self.start_urls.append('http://www.moneycontrol.com/news/business/page-'+ str(count))

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))

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
            #item['source'] = 108
            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                self.custom_settings['url_stats']['scraped'] += 1
                yield item
            else:
                self.custom_settings['url_stats']['dropped'] += 1
                yield None

    def getPageContent(self, newsBox):
        data = newsBox.xpath('p/text()').extract_first()
        if (data is None):
            data = newsBox.xpath('h2/a/@title').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageTitle(self, newsBox):
        data = newsBox.xpath('h2/a/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = newsBox.xpath('a/@href').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath('a/img/@src').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        data = newsBox.xpath('span/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
