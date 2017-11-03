# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem

class IndianexpresstechSpider(scrapy.Spider):
    name = 'indianExpressTech'
    allowed_domains = ['indianexpress.com']
    start_urls = ['http://indianexpress.com/section/technology/']


    def parse(self, response):
        newsContainer = response.xpath('//div[@class="top-article"]/ul[@class="article-list"]/li')
        for newsBox in newsContainer:
            link = newsBox.xpath('figure/a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.parse_article)


    def parse_article(self,response):
        item = ScrapenewsItem() #Scraper Items
        item['image']  = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['date'] = self.getPageDate(response)
        item['link'] = self.getPageLink(response)
        yield item


    def getPageContent(self, response):
        data = response.xpath('//h2[@class="synopsis"]/text()').extract_first()
        if (data is None):
            print('Error 101: ',response.url)
            data = 'Error'
        return data


    def getPageTitle(self, response):
        data = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        if (data is None):
            print('Error 102: ',response.url)
            data = 'Error'
        return data


    def getPageLink(self, response):
        data = response.url
        if (data is None):
            print('Error 103: ',response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath('//span[@class="custom-caption"]/img/@data-lazy-src').extract_first()
        if (data is None):
            print('Error 104: ',response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
             data = ''.join((str(response.xpath('//span[@itemprop="dateModified"]/text()').extract_first()).split('Published:')[1]).split("'")[0]) #Relax, This line Will parse the date and remove unnecessary details out of the string provided!
        except IndexError:
            try:
                data = ''.join((str(response.xpath('//span[@itemprop="dateModified"]/text()').extract_first()).split('Updated: ')[1]).split("'")[0]) #Relax, This line Will parse the date and remove unnecessary details out of the string provided!
            except IndexError:
                print('Error 105: ',response.url)
                data = 'Error'
        finally:
            return data
