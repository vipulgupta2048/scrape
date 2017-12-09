# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


class FirstpostsportsSpider(scrapy.Spider):

    name = 'firstpostSports'
    allowed_domains = ['firstpost.com']
    custom_settings = {
        'site_id':112,
        'site_name':'firstpost(sports)',
        'site_url':'http://www.firstpost.com/category/sports/'}

    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(FirstpostsportsSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.firstpost.com/category/sports/page/'+ str(count+1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        newsContainer = response.xpath("//ul[@class='articles-list']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article)


    def parse_article(self, response):
        if (str(response.url)[:32] != "http://www.firstpost.com/photos/"):
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 112
            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                yield item


    def getPageTitle(self, response):
        try:
            data = ' '.join(response.xpath("//h1[@itemprop='headline']/text()").extract_first().split())
        except AttributeError as Error:
            data = response.xpath('//h1[@class="story-title"]/text()').extract_first()
            if (data is None):
                data = response.xpath('//h1[@class="page-title article-title"]/text()').extract_first()
            if (data is None):
                loggerError.error(Error, response.url)
                data = 'Error'
        except Exception as Error:
            loggerError.error(Error, response.url)
            data = 'Error'
        finally:
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
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(Error, response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = ' '.join((' '.join(response.xpath("//div[contains(@class,'article-full-content')]/p/text()").extract())).split(' ')[:40])
        if not data:
            loggerError.error(Error, response.url)
            data = 'Error'
        return data
