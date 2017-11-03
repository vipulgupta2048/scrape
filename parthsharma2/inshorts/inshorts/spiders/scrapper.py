# -*- coding: utf-8 -*-
import scrapy
import re
import json
import lxml


class ScrapperSpider(scrapy.Spider):
    name = 'scrapper'
    allowed_domains = ['https://www.inshorts.com/en/read']
    start_urls = ['https://www.inshorts.com/en/read/']

    def __init__(self, pages=1, *args, **kwargs):
        super(ScrapperSpider, self).__init__(*args, **kwargs)
        self.pages = int(pages)

    def parse(self, response):

        for news in response.css('div.news-card'):
            item = {
                'title': news.css('a.clickable>span::text').extract_first(),
                'author': news.css('span.author::text').extract_first(),
                'time': news.css('span.time::text').extract_first(),
                'date': news.css('span[clas*=date]::text').extract_first(),
                'content': news.css('div[itemprop*=articleBody]::text').extract_first(),
                'link' : news.css('div.read-more>a::attr(href)')
            }

            yield item

        self.extract_more_news()


    def extract_more_news(self):
        pattern = re.compile('var min_news_id\s+=\s+"(.*?)"')
        script = response.css('script[type*="text/javascript"]').extract()[-1]
        try:
            id = pattern.search(script).group(1)
        except:
            id = response['min_news_id']
        r = scrapy.FormRequest('https://www.inshorts.com/en/ajax/more_news', formdata={'news_offset':id})
        scrapy.fetch(r)
        contents = json.loads(response.text)
        html = lxml.html.fromstring(contents['html'])
        for news in lxml.cssselect('div.news-card'):
            item = {
                'title': news.cssselect('a.clickable>span::text').extract_first(),
                'author': news.css('span.author::text').extract_first(),
                'time': news.css('span.time::text').extract_first(),
                'date': news.css('span[clas*=date]::text').extract_first(),
                'content': news.css('div[itemprop*=articleBody]::text').extract_first(),
                'link' : news.css('div.read-more>a::attr(href)')
            }

            yield item
