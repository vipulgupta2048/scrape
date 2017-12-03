# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.db import LogsManager

class InshortsSpider(scrapy.Spider):
    name = 'inshorts'
    allowed_domains = ['www.inshorts.com/en/read']
    start_urls = ['http://www.inshorts.com/en/read/']
    custom_settings = {
        'site_id':105,
        'site_name':'Inshorts',
        'site_url':'http://www.inshorts.com/en/read/'}


    custom_settings = {
        'site_name': "Inshorts",
        'site_url': "http://www.inshorts.com/en/read/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    def parse(self, response):
        for news in response.css('div.news-card'):
            item = ScrapenewsItem()
            self.custom_settings['url_stats']['parsed'] += 1
            item['image'] = news.css('div.news-card-image::attr(style)').extract_first()[23:-3]
            item['title'] = news.css('a.clickable>span::text').extract_first()
            item['content'] = news.css('div[itemprop*=articleBody]::text').extract_first()
            item['newsDate'] = news.css('span.time::attr(content)').extract_first()[:-5]
            item['link'] = news.css('div.read-more>a::attr(href)').extract_first()
            #item['source'] = 105
            self.custom_settings['url_stats']['scraped'] += 1
            yield item

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
