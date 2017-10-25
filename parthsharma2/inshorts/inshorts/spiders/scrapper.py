# -*- coding: utf-8 -*-
import scrapy


class ScrapperSpider(scrapy.Spider):
    name = 'scrapper'
    allowed_domains = ['https://www.inshorts.com/en/read']
    start_urls = ['https://www.inshorts.com/en/read/']

    def parse(self, response):
        for news in response.css('div.news-card'):
            item = {
                'headline': news.css('a.clickable>span::text').extract_first(),
                'author': news.css('span.author::text').extract_first(),
                'time': news.css('span.time::text').extract_first(),
                'date': news.css('span[clas*=date]::text').extract_first(),
                'body': news.css('div[itemprop*=articleBody]::text').extract_first(),
            }

            yield item
