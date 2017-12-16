# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


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

    def closed(self, reason):
        self.postgres.closeConnection(reason)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))

    def parse(self, response):
        newsContainer = response.xpath("//ul[@class='newsListfull']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)


    def parse_article(self, response):
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


    def getPageTitle(self, response):
        data = response.xpath('//h1[@class="arttitle"]/text()').extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath('//div[@class="content"]/div/figure/img/@src').extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = response.xpath("//span[@class='dattime']/text()").extract()[1].rsplit(' ', 3)[0]
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data


    def getPageContent(self, response):
        data = ' '.join(response.xpath("//div[@class='content']/p/text()").extract())
        if not data:
            loggerError.error(response.url)
            data = 'Error'
        return data
