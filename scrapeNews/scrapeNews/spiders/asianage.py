# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from time import sleep

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

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)
            sleep(2)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        item = ScrapenewsItem()  # Scraper Items
        newsContainer = response.xpath("//div[contains(@class,'india-news')]/div[@class='singlesunday']")
        for newsBox in newsContainer:
            item['image'] = self.getPageImage(newsBox)
            if not self.postgres.checkUrlExists(item['link']):
                item['title'] = self.getPageTitle(newsBox)
                item['content'] = self.getPageContent(newsBox)
                item['newsDate'] = self.getPageDate(newsBox)
                item['link'] = self.getPageLink(newsBox)
                item['source'] = 115
                if item['title'] is not 'Error' and item['content'] is not 'Error' and item['link'] is not 'Error' and item['newsDate'] is not 'Error':
                    self.urls_scraped += 1
                    yield item

    def getPageContent(self, newsBox):
        data = newsBox.xpath('div/p[@class="These"]/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageTitle(self, newsBox):
        data = newsBox.xpath('div/h2/a/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = 'http://www.asianage.com/newsmakers' + newsBox.xpath('div/a/@href').extract_first()
        if (data == 'http://www.asianage.com/newsmakers'):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath('div/a/img/@data-src').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        data = newsBox.xpath('div/p[@class="newDate"]/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.extract())
            data = 'Error'
        return data
