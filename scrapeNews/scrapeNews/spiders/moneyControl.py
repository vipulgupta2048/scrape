# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


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
            item['link'] = self.getPageLink(newsBox)
            if not self.postgres.checkUrlExists(item['link']):
                item['image'] = self.getPageImage(newsBox)
                item['title'] = self.getPageTitle(newsBox)
                item['content'] = self.getPageContent(newsBox)
                item['newsDate'] = self.getPageDate(newsBox)
                item['source'] = 108
                if item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                    self.urls_scraped += 1
                    yield item

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
