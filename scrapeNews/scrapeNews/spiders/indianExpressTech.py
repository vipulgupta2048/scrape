# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from scrapeNews.db import DatabaseManager, LogsManager

class IndianexpresstechSpider(scrapy.Spider):

    name = 'indianExpressTech'
    allowed_domains = ['indianexpress.com']
    custom_settings = {
        'site_id': 101,
        'site_name': 'Indian Express',
        'site_url': 'http://indianexpress.com/section/technology/'}

    custom_settings = {
        'site_name': "Indian Express",
        'site_url': "http://indianexpress.com/section/technology/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }


    def __init__(self, offset=0, pages=2, *args, **kwargs):
        #self.postgres = pipeline()
        #self.postgres.openConnection()
        super(IndianexpresstechSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://indianexpress.com/section/technology/page/'+ str(count+1))

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))

    def spider_closed(self, spider):
        #self.postgres.closeConnection()
        return True

    def parse(self, response):
        newsContainer = response.xpath('//div[@class="top-article"]/ul[@class="article-list"]/li')
        for newsBox in newsContainer:
            link = newsBox.xpath('figure/a/@href').extract_first()
            if not DatabaseManager().urlExists(link):
                self.custom_settings['url_stats']['parsed'] += 1
                yield scrapy.Request(url=link, callback=self.parse_article)
            else:
                self.custom_settings['url_stats']['dropped'] += 1


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        #item['source'] = 101
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None

    def getPageContent(self, response):
        data = response.xpath('//h2[@class="synopsis"]/text()').extract_first()
        if (data is None):
            data = response.xpath("//div[@class='full-details']/p/text()").extract_first()
        if (data is None):
            data = ' '.join(' '.join(response.xpath("//div[@class='body-article']/p/text()").extract()).split()[:40])
        if not data:
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath('//span[@class="custom-caption"]/img/@data-lazy-src').extract_first()
        if (data is None):
            data = response.xpath("//span[@itemprop='image']/meta[@itemprop='url']/@content").extract_first()
        if (data is None):
            try:
                data = ((response.xpath('//div[@class="lead-article"]/@style').extract_first()).split('url(',1)[1]).split(')',1)[0]
            except Exception as Error:
                loggerError.error(str(Error) + " occured at: " + response.url)
                data = 'Error'
        return data

    def getPageDate(self, response):
        data = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if (data is None):
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data
    
    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
