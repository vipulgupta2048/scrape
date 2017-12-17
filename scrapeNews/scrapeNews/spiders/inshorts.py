# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapy.http import FormRequest
from scrapy.selector import Selector
import json
import re


class InshortsSpider(scrapy.Spider):
    name = 'inshorts'
    allowed_domains = ['www.inshorts.com']
    start_urls = ['http://www.inshorts.com/en/read/']
    DUPEFILTER_DEBUG = False
    custom_settings = {
        'site_id':105,
        'site_name':'Inshorts',
        'site_url':'http://www.inshorts.com/en/read/'}

    def __init__(self, pages=3, toInfinityAndBeyond=False ,*args, **kwargs):
        '''
        Set 'pages' to set the number of pages to scrape [Default=3]
        Set 'toInfinityAndBeyond' to set infinite scraping [Default=False]
        '''
        super(InshortsSpider, self).__init__(*args, **kwargs)
        self.infinite = (toInfinityAndBeyond == "True")
        self.pages = int(pages)
        self.news_id = ''

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('ERROR: ' + str(failure.request.url))

    def parse(self, response):
        for news in response.css('div.news-card'):
            item = ScrapenewsItem()
            item['image'] = news.css('div.news-card-image::attr(style)').extract_first()[23:-3]
            item['title'] = news.css('a.clickable>span::text').extract_first()
            item['content'] = news.css('div[itemprop*=articleBody]::text').extract_first()
            item['newsDate'] = news.css('span.time::attr(content)').extract_first()[:-5]
            item['link'] = news.css('div.read-more>a::attr(href)').extract_first()
            item['source'] = 105
            yield item

        #news_id extraction
        pattern = re.compile('var min_news_id\s+=\s+"(.*?)"')
        js = response.xpath('//script[@type="text/javascript"]/text()').extract()[-1]
        self.news_id = pattern.search(js).group(1)

        while (self.pages > 1 and not self.infinite):
            yield FormRequest('https://www.inshorts.com/en/ajax/more_news',
                                formdata={'news-offset' : self.news_id},
                                callback=self.parse_more_news,
                                errback=self.errorRequestHandler,
                                dont_filter=True)
            self.pages -= 1

        while (self.infinite):
            yield FormRequest('https://www.inshorts.com/en/ajax/more_news',
                                formdata={'news-offset' : self.news_id},
                                callback=self.parse_more_news,
                                errback=self.errorRequestHandler,
                                dont_filter=True)

    def parse_more_news(self, response):
        ajax_response = json.loads(response.text)
        self.news_id = ajax_response['min_news_id']
        html = Selector(text=ajax_response['html'])
        for news in html.css('div.news-card'):
            item = ScrapenewsItem()
            item['image'] = news.css('div.news-card-image::attr(style)').extract_first()[23:-3]
            item['title'] = news.css('a.clickable>span::text').extract_first()
            item['content'] = news.css('div[itemprop*=articleBody]::text').extract_first()
            item['newsDate'] = news.css('span.time::attr(content)').extract_first()[:-5]
            item['link'] = news.css('div.read-more>a::attr(href)').extract_first()
            item['source'] = 105
            yield item

    def closed(self, reason):
        self.postgres.closeConnection(reason)
