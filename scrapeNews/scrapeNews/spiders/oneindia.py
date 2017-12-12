# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


class OneindiaSpider(scrapy.Spider):

    name = 'oneindia'
    allowed_domains = ['oneindia.com']
    custom_settings = {
        'site_id':109,
        'site_name':'oneindia',
        'site_url':'https://www.oneindia.com/india/'}

    def __init__(self, offset=0, pages=2, *args, **kwargs):
        super(OneindiaSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('https://www.oneindia.com/india/?page-no='+ str(count+1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def parse(self, response):
        newsContainer = response.xpath('//div[@id="collection-wrapper"]/article')
        for newsBox in newsContainer:
            link = 'https://www.oneindia.com/india/' + newsBox.xpath('div/h2/a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article)


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        item['source'] = 109
        self.urls_scraped += 1
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item


    def getPageContent(self, response):
        data = ' '.join((''.join(response.xpath("//div[contains(@class,'io-article-body')]/p/text()").extract())).split(' ')[:40])
        if not data:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath("//h1[contains(@class,'heading')]/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = 'https://www.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@data-pagespeed-lazy-src").extract_first()
        if (data == 'https://www.oneindia.com'):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            data = (response.xpath("/html/head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data
