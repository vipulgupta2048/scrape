# -*- coding: utf-8 -*-
import scrapy


class InshortsScraperSpider(scrapy.Spider):
    name = 'inshorts_scraper'
    allowed_domains = ['www.inshorts.com/en/read']
    start_urls = ['http://www.inshorts.com/en/read/']

    def __init__(self, pages=1, *args, **kwargs):
        super(InshortsScraperSpider, self).__init__(*args, **kwargs)
        self.pages = int(pages)

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

        while self.pages > 1:
            pattern = re.compile('var min_news_id\s+=\s+"(.*?)"')
            script = response.css('script[type*="text/javascript"]').extract()[-1]
            id = pattern.search(script).group(1)
            r = scrapy.FormRequest('https://www.inshorts.com/en/ajax/more_news', callback=self.parse, formdata={'news_offset':id})
            yield scrapy.fetch(r)
            self.pages -= 1


    def extract_more_news(self, response):
        pass
