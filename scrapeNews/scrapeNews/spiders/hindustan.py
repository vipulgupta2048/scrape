# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.db import DatabaseManager, LogsManager

class HindustanSpider(scrapy.Spider):


    name = 'hindustan'
    allowed_domains = ['www.hindustantimes.com']

    custom_settings = {
        'site_name': "hindustantimes",
        'site_url': "http://www.hindustantimes.com/editors-pick/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    temp = 'http://www.hindustantimes.com/Fragment/HT/Web/Components/home-editors-pick.dwc?style=/PortalConfig/www.ns.hindustantimes.com/jpt-ns/include/fragments/show-more-fragment.jpt&offset='
    start_urls = [temp+'1']
    count = 1
    def parse(self, response):
        something = response.css('div.media')
        for somethings in something:
            link = somethings.xpath('.//div[contains(@class,"media-body")]/div[1]/a/@href').extract_first()
            if not DatabaseManager().urlExists(link):
                self.custom_settings['url_stats']['parsed'] += 1
                yield scrapy.Request(url=link, callback=self.fun)
            else:
                self.custom_settings['url_stats']['dropped'] += 1
        self.count += 1
        #print(self.count)
        yield scrapy.Request(url=self.temp+str(self.count), callback=self.parse)

    def fun(self, response):
        text = response.text
        headline = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        images = response.xpath('//div[@class="thumbnail"]/img/@src').extract_first()
        body = response.xpath('//div[@itemprop="articlebody"]/p').extract_first()
        date = response.css('span.text-dt::text').extract_first()
        
        item = ScrapenewsItem({'title': headline, 'link': response.url, 'newsDate': date, 'content': body, 'image': images})

        self.custom_settings['url_stats']['scraped'] += 1
        yield item
    
    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)

        item = ScrapenewsItem({'title': headline, 'link': response.url, 'newsDate': date, 'content': body, 'image': images,  'source': 114 })
        self.urls_scraped += 1
        yield item
