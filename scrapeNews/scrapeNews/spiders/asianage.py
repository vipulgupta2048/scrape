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

    def __init__(self, offset=0, pages=10, *args, **kwargs):
        super(AsianageSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.asianage.com/newsmakers?pg='+ str(count+1))

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        newsContainer = response.xpath("//div[@class='singlesunday']")
        for newsBox in newsContainer:
            link = 'http://www.asianage.com' + newsBox.xpath('div/h2/a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)


    def parse_article(self, response):
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


    def getPageTitle(self, response):
        data = response.xpath("head/title/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first())
        except Exception as Error:
            loggerError.error(Error, response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = ' '.join(response.xpath("//div[@id='storyBody']/p/text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[@id='storyBody']/p//text()").extract())
        if not data:
            loggerError.error(response.url)
            data = 'Error'
        return data
