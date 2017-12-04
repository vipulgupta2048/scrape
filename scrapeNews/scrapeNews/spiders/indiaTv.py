# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.pipelines import InnerSpiderPipeline as pipeline
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


class IndiatvSpider(scrapy.Spider):

    name = 'indiaTv'
    allowed_domains = ['www.indiatvnews.com']
    custom_settings = {
        'site_id':102,
        'site_name':'India TV',
        'site_url':'http://www.indiatvnews.com/business/tech/'}


    def __init__(self, offset=0, pages=3, *args, **kwargs):
        self.postgres = pipeline()
        self.postgres.openConnection()
        super(IndiatvSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.indiatvnews.com/india/' + str(count + 1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IndiatvSpider,cls).from_crawler(crawler,*args,**kwargs)
        crawler.signals.connect(spider.spider_closed,scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        self.postgres.closeConnection()


    def parse(self, response):
        newsContainer = response.xpath("//ul[@class='newsListfull']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article)


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        item['source'] = 102
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
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
        try:
            data = ' '.join((' '.join(response.xpath("//div[@class='content']/p/text()").extract())).split(' ')[:40])
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data
