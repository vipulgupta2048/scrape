# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from datetime import datetime

class nation(scrapy.Spider):
    name = "nnation"
    start_urls = ['http://www.newsnation.in/business-news',]
    #allowed_domains = ['http://www.newsnation.in/business-news']
    custom_settings = {
        'site_id':117,
        'site_name':'newsnation',
        'site_url':'http://www.newsnation.in/business-news'}
    
    def closed(self, reason):
        self.postgres.closeConnection(reason)
    
    #Scraping the main page for article links
    def parse(self,response):
        newsBox = response.xpath('//ul[contains(@class, "ciln")]/li')
        for box in newsBox:
            link = box.xpath('./div[2]/h2/a/@href').extract_first()
            yield response.follow(link, callback = self.parse_article)

        #For scraping the links on the next page of the website
        next_page = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_page is not None:
            print("==============Switching Page======================")
            yield response.follow(next_page, callback = self.parse)

    #For scraping a particular article listed on the main page
    def parse_article(self,response):
        i = ScrapenewsItem()
        i['title'] = self.gettitle(response)
        i['link'] = response.url
        i['image'] = self.getimage(response)
        i['newsDate'] = self.getdatetime(response)
        i['content'] = self.getcontent(response)
        i['source'] = 117
        
        yield i

    def gettitle(self,response):
        data = response.xpath("//h1/text()").extract_first() 
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data   

    def getdatetime(self,response):
        data = response.xpath('//span[contains(@itemprop, "date")]/text()').extract_first() 
        z = (datetime.strptime(data," %d %b , %Y , %H:%M %p")).strftime("%Y-%m-%d %H:%M:%S")
        if (z is None):
            loggerError.error(response.url)
            data = 'Error'
        return data   

    def getcontent(self,response):
        data = response.xpath('//div[@itemprop ="articleBody"]//p/text()').extract()
        if not data:
            data = response.xpath('//div[@itemprop ="articleBody"]//span/text()').extract()
        if not data:    
            loggerError.error(response.url)
            data = 'Error'
        if data is none: 
            yield none
        return data

    def getimage(self,response):
        data = response.xpath('//div[contains(@itemprop, "image")]//img/@src').extract_first()
        if not data:    
            loggerError.error(response.url)
            data = 'Error'
        return data
