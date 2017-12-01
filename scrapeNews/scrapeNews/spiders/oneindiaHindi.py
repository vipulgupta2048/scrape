# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.pipelines import InnerSpiderPipeline as pipeline
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


# Setting up local variables USERNAME & PASSWORD
PASSWORD = envConfig.PASSWORD
USERNAME = envConfig.USERNAME

class OneindiahindiSpider(scrapy.Spider):

    name = 'oneindiaHindi'
    allowed_domains = ['oneindia.com']


    def __init__(self, offset=0, pages=4, *args, **kwargs):
        super(OneindiahindiSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('https://hindi.oneindia.com/news/india/?page-no='+ str(count+1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        postgres = pipeline()
        postgres.openConnection()
        newsContainer = response.xpath('//div[@id="collection-wrapper"]/article')
        for newsBox in newsContainer:
            link = 'https://hindi.oneindia.com/news/india/' + newsBox.xpath('div/h2/a/@href').extract_first()
            if not postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article)
        postgres.closeConnection()

    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        item['source'] = 110
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item


    def getPageContent(self, response):
        try:
            data = ' '.join((''.join(response.xpath("//div[contains(@class,'io-article-body')]/p/text()").extract())).split(' ')[:40])
        except:
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath("//h1[contains(@class,'heading')]/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@src").extract_first()
        if (data is None):
            data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@data-pagespeed-lazy-src").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            data = (response.xpath("//time/@datetime").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data
