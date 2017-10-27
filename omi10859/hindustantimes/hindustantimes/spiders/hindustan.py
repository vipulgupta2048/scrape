# -*- coding: utf-8 -*-
import scrapy


class HindustanSpider(scrapy.Spider):
    name = 'hindustan'
    allowed_domains = ['www.hindustantimes.com']
    start_urls = ['http://www.hindustantimes.com/editors-pick']

    def parse(self, response):
        for news in response.css('div.media'):
            item = {
                'hedline': news.css('div.media-heading>a::text').extract_first(), 
                'date' : news.css('div>span.time-dt::text').extract_first(), 
                'para' : news.css('div.para-txt::text').extract_first(), 

            }

            yield item