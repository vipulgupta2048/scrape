# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import logging
logger = logging.getLogger("scrapeNews")


class IndianexpresstechSpider(scrapy.Spider):
    name = 'indianExpressTech'
    allowed_domains = ['indianexpress.com']

    def __init__(self, pages=2, *args, **kwargs):
        super(IndianexpresstechSpider, self).__init__(*args, **kwargs)
        for count in range(1 , int(pages)+1):
            self.start_urls.append('http://indianexpress.com/section/technology/page/'+ str(count))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        newsContainer = response.xpath('//div[@class="top-article"]/ul[@class="article-list"]/li')
        for newsBox in newsContainer:
            link = newsBox.xpath('figure/a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.parse_article)

    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = self.getPageLink(response)
        item['source'] = 101
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item

    def getPageContent(self, response):
        data = response.xpath('//h2[@class="synopsis"]/text()').extract_first()
        if (data is None):
            data = response.xpath("//div[@class='full-details']/p/text()").extract_first()
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data

    def getPageLink(self, response):
        data = response.url
        if (data is None):
            logger.critical(response)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath('//span[@class="custom-caption"]/img/@data-lazy-src').extract_first()
        if (data is None):
            data = response.xpath("//span[@itemprop='image']/meta[@itemprop='url']/@content").extract_first()
        if (data is None):
            logger.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # Relax, This line Will parse the date and remove unnecessary
            # details out of the string provided!
            data = ''.join((str(response.xpath('//span[@itemprop="dateModified"]/text()').extract_first()).split('Published:')[1]).split("'")[0].split('\t')[0].split(' ',1)[1])
        except IndexError:
            try:
                # Relax, This line Will parse the date and remove unnecessary
                # details out of the string provided!
                data = ''.join((str(response.xpath('//span[@itemprop="dateModified"]/text()').extract_first()).split('Updated: ')[1]).split("'")[0].split('\t')[0])
            except IndexError:
                logger.error(response.url)
                data = 'Error'
        finally:
            return data
