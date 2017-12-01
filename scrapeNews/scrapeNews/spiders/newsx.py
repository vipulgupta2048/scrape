# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.pipelines import InnerSpiderPipeline as pipeline
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


# Setting up local variables USERNAME & PASSWORD
PASSWORD = envConfig.PASSWORD
USERNAME = envConfig.USERNAME

class NewsxSpider(scrapy.Spider):

    name = 'newsx'
    allowed_domains = ['newsx.com']
    start_urls = ['http://newsx.com/']


    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(NewsxSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.newsx.com/latest-news/page/'+ str(count+1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        postgres = pipeline()
        postgres.openConnection()
        newsContainer = response.xpath("//div[contains(@class,'cat-grid-gap')]/div[@class='well ft2']")
        for newsBox in newsContainer:
            link = newsBox.xpath('div/a/@href').extract_first()
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
        item['source'] = 113
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item


    def getPageTitle(self, response):
        try:
            data = ' '.join(response.xpath("//h1[@itemprop='headline']/text()").extract_first().split())
        except AttributeError as Error:
            loggerError.error(response.url)
            data = 'Error'
        finally:
            return data

    def getPageImage(self, response):
        data = response.xpath("//head/link[@rel='image_src']/@href").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@itemprop='datePublished']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(Error, response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = response.xpath("//div[@class='story-short-title']/h2/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data
