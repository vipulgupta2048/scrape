# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import logging
import envConfig
import psycopg2
loggerError = logging.getLogger("scrapeNewsError")

# Setting up local variables USERNAME & PASSWORD
PASSWORD = envConfig.PASSWORD
USERNAME = envConfig.USERNAME


class IndiatvSpider(scrapy.Spider):
    name = 'indiaTv'
    allowed_domains = ['www.indiatvnews.com']


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IndiatvSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, scrapy.signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, scrapy.signals.spider_opened)
        return spider


    def __init__(self, offset=0, pages=2, *args, **kwargs):
        super(IndiatvSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.indiatvnews.com/india/'+ str(count+1))


    def spider_opened(self, spider):
        self.connection = psycopg2.connect(
        host='localhost',
        user=USERNAME,
        database='scraped_news',
        password=PASSWORD)
        self.cursor = self.connection.cursor()


    def spider_closed(self, spider):
        self.cursor.close()
        self.connection.close()


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        newsContainer = response.xpath("//ul[@class='newsListfull']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('a/@href').extract_first()
            self.cursor.execute("""SELECT link from news_table where link= %s """, (link,))
            if not self.cursor.fetchall():
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
            data = response.xpath("//span[@class='dattime']/text()").extract()[1].rsplit(' ',3)[0]
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
