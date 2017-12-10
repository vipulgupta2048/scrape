# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem


class InshortsSpider(scrapy.Spider):
    name = 'inshorts'
    allowed_domains = ['www.inshorts.com/en/read']
    start_urls = ['http://www.inshorts.com/en/read/']
    custom_settings = {
        'site_id':105,
        'site_name':'Inshorts',
        'site_url':'http://www.inshorts.com/en/read/'}


    def parse(self, response):
        for news in response.css('div.news-card'):
            self.urls_parsed += 1
            item = ScrapenewsItem()
            item['image'] = news.css('div.news-card-image::attr(style)').extract_first()[23:-3]
            item['title'] = news.css('a.clickable>span::text').extract_first()
            item['content'] = news.css('div[itemprop*=articleBody]::text').extract_first()
            item['newsDate'] = news.css('span.time::attr(content)').extract_first()[:-5]
            item['link'] = news.css('div.read-more>a::attr(href)').extract_first()
            item['source'] = 105
            self.urls_scraped += 1

            yield item

    def closed(self, reason):
        self.postgres.closeConnection(reason)
