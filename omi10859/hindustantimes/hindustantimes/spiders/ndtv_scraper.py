# -*- coding: utf-8 -*-
import scrapy
import time
import logging


class NdtvScraperSpider(scrapy.Spider):
    name = 'ndtv_scraper'
    start_urls = ['http://www.ndtv.com/latest/']

    def __init__(self, pages=1, *args, **kwargs):
        super(NdtvScraperSpider, self).__init__(*args, **kwargs)
        self.pages = pages

    def parse(self, response):
        #for news in response.css('div.new_storylising>ul>li'):
        #    try:
        #        item = {
        #            'headline': news.css('div.nstory_header>a::text').extract_first(),
        #            'author': news.css('div.nstory_dateline>a::text').extract_first(),
        #            'date': news.css('div.nstory_dateline::text').extract()[-1].strip()[2:],
        #            'content': news.css('div.nstory_intro::text').extract_first(),
        #        }
        #    except AttributeError:
        #        pass
        #    yield item

        page_ctr = 1
        while page_ctr <= int(self.pages):
            time.sleep(2)
            next_page = 'http://www.ndtv.com/latest/page-' + str(page_ctr)
            yield scrapy.Request(next_page, callback=self.parse_news)
            page_ctr += 1

    def parse_news(self, response):
        for news in response.css('div.new_storylising>ul>li'):
            item = {
                    'title': news.css('div.nstory_header>a::text').extract_first(),
                    'date': news.css('div.nstory_dateline::text').extract(),
                    'content': news.css('div.nstory_intro::text').extract_first(),
                    'link': news.css('div.nstory_header>a::attr(href)').extract_first(),
                    'image': news.css('div.new_storylising_img>a>img::attr(src)').extract_first(),
                }

            yield item
