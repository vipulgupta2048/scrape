# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from requests import get as parsePage
from lxml import etree, html


class IndiatvSpider(scrapy.Spider):
    name = 'indiaTv'
    allowed_domains = ['www.indiatvnews.com/business/tech']
    start_urls = ['http://www.indiatvnews.com/business/tech/']

    def parse(self, response):
        newsContainer = response.xpath('//div[contains(@class,"topNews")]/ul[@class="newsListfull"]/li')

        for newsBox in newsContainer:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(newsBox)
            item['title'] = self.getPageTitle(newsBox)
            item['content'] = self.getPageContent(newsBox)
            item['newsDate'] = self.getPageDate(newsBox)
            item['link'] = self.getPageLink(newsBox)
            item['source'] = 102
            yield item

    def getPageTitle(self, newsBox):
        data = newsBox.xpath("div[@class='content']/h3[@class='title']/a/text()").extract_first()
        if (data is None):
            print('Error 301: ', newsBox.extract())
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = newsBox.xpath("a[@class='thumb']/@href").extract_first()
        if (data is None):
            print('Error 302: ', newsBox.extract())
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath("a[@class='thumb']/img/@data-original").extract_first()
        if (data is None):
            print('Error 303: ', newsBox.extract())
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = newsBox.xpath("div[@class='content']/span[@class='deskTime']/text()").extract_first().split('|')[1].rsplit(' ', 1)[0]
        except IndexError:
            print('Error 304: ', newsBox.extract())
            data = 'Error'
        finally:
            return data

    def getPageContent(self, newsBox):
        data = newsBox.xpath("div[@class='content']/p[@class='dic']/text()").extract_first()
        if (data is None):
            try:
                newsPage = parsePage(self.getPageLink(newsBox)).text
                et = html.fromstring(newsPage)
                # Relax, This takes in all the paragraphs from the page and
                # spit out first 30 words in a string!
                data = ' '.join(str(et.xpath("//div[@class='content']/p/text()")).split(' ')[:30])
            except Exception as Error:
                print('Error 305: ', Error)
                data = 'Error'
        return data
