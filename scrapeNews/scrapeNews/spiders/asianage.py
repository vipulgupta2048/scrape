# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError

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
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        newsContainer = response.xpath("//div[contains(@class,'india-news')]/div[@class='singlesunday']")
        for newsBox in newsContainer:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(newsBox)
            item['title'] = self.getPageTitle(newsBox)
            item['content'] = self.getPageContent(newsBox)
            item['newsDate'] = self.getPageDate(newsBox)
            item['link'] = self.getPageLink(newsBox)
            item['source'] = 115
            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                yield item

    def getPageContent(self, newsBox):
        data = newsBox.xpath('div/p[@class="These"]/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.url)
            data = 'Error'
        return data

    def getPageTitle(self, newsBox):
        data = newsBox.xpath('div/h2/a/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.url)
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = 'http://www.asianage.com/newsmakers' + newsBox.xpath('div/a/@href').extract_first()
        if (data is None):
            loggerError.error(newsBox)
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath('div/a/img/@data-src').extract_first()
        if (data is None):
            loggerError.error(newsBox.url)
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        data = newsBox.xpath('div/p[@class="newDate"]/text()').extract_first()
        if (data is None):
            loggerError.error(newsBox.url)
            data = 'Error'
        return data
