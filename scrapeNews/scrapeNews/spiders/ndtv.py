# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import time
import logging


class NdtvSpider(scrapy.Spider):
    name = 'ndtv'
    start_urls = ['http://www.ndtv.com/latest/']

    def __init__(self, pages=1, *args, **kwargs):
        super(NdtvSpider, self).__init__(*args, **kwargs)
        self.pages = pages

    def parse(self, response):
        page_ctr = 1
        while page_ctr <= int(self.pages):
            time.sleep(2)
            next_page = 'http://www.ndtv.com/latest/page-' + str(page_ctr)
            yield scrapy.Request(next_page, callback=self.parse_news)
            page_ctr += 1

    def parse_news(self, response):
        for news in response.css('div.new_storylising>ul>li'):
                item = ScrapenewsItem()  # Scraper Items
                if news.css('div.nstory_header>a::text'):
                    item['image'] = news.css('div.new_storylising_img>a>img::attr(src)').extract_first()
                    item['title'] = news.css('div.nstory_header>a::text').extract_first().strip()
                    item['content'] = news.css('div.nstory_intro::text').extract_first()
                    item['newsDate'] = news.css('div.nstory_dateline::text').extract()[-1].strip()[2:]
                    item['link'] = news.css('div.nstory_header>a::attr(href)').extract_first()
                    item['source'] = 104
                    yield item
                else:
                    logging.debug('Skipping a News Item, most probably an Advertisment')
