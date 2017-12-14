# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
import requests
from lxml import html
from datetime import datetime


class NdtvSpider(scrapy.Spider):

    name = 'ndtv'
    start_urls = ['http://www.ndtv.com/latest/']
    custom_settings = {
        'site_id': 104,
        'site_name': 'NDTV',
        'site_url': 'https://www.ndtv.com/latest/page-1'}
    download_delay = 2

    def __init__(self, pages=1, *args, **kwargs):
        super(NdtvSpider, self).__init__(*args, **kwargs)
        self.pages = pages
        for count in range(0, int(pages)):
            self.start_urls.append('http://www.ndtv.com/latest/page-' + str(count + 1))

    def closed(self, reason):
        self.postgres.closeConnection(reason)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_news, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('ERROR: ' + str(failure.request.url))

    def parse_news(self, response):
        item = ScrapenewsItem()  # Scraper Items
        for news in response.xpath('//div[@class="new_storylising"]/ul/li'):
                if news.xpath('.//div[@class="nstory_header"]/a/text()'):
                    item['image'] = news.xpath('.//img/@src').extract_first()
                    item['title'] = news.xpath('.//div[@class="nstory_header"]/a/text()').extract_first().strip()
                    item['content'] = news.xpath('.//div[@class="nstory_intro"]/text()').extract_first()
                    item['link'] = news.xpath('.//div[@class="nstory_header"]/a/@href').extract_first()
                    item['newsDate'] = self.parse_date(item['link'])
                    item['source'] = 104
                    yield item

    def parse_date(self, link):
        page = requests.get(link)
        r = html.fromstring(page.content)
        if r.xpath('//span[@itemprop="dateModified"]/@content'):
            return r.xpath('//span[@itemprop="dateModified"]/@content')[0][:-6]
        elif r.xpath('//meta[@name="publish-date"]/@content'):
            try :
                date = r.xpath('//meta[@name="publish-date"]/@content')[0][:-6]
                date = (datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')).strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                date = r.xpath('//meta[@name="publish-date"]/@content')[0][:-6]
                date = (datetime.strptime(date, '%a,%d %b %Y %H:%M:%S')).strftime("%Y-%m-%dT%H:%M:%S")
            return date
        elif r.xpath('//meta[@itemprop="dateModified"]/@content'):
            return r.xpath('//meta[@itemprop="dateModified"]/@content')[0][:-6]
        else :
            loggerError.error('NDTV ADD THIS: ' + link)
            return None
