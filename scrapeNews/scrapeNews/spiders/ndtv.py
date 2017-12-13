# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import time
from scrapeNews.settings import logger
import requests
from lxml import html
from datetime import datetime
from scrapeNews.db import LogsManager

class NdtvSpider(scrapy.Spider):


    name = 'ndtv'
    start_url = 'http://www.ndtv.com/latest/page-'
    page_counter = 1

    custom_settings = {
        'site_name': "NDTV",
        'site_url': "https://www.ndtv.com/latest/page-1",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    def start_requests(self):
        yield scrapy.Request(self.start_url + str(self.page_counter), self.parse)

    def parse(self, response):
        if response.status == 200:
            try:
                item = ScrapenewsItem()  # Scraper Items
                for news in response.css('div.new_storylising>ul>li'):
                    if news.css('div.nstory_header>a::text'):
                        self.custom_settings['url_stats']['parsed'] += 1
                        item['image'] = news.css('div.new_storylising_img>a>img::attr(src)').extract_first()
                        item['title'] = news.css('div.nstory_header>a::text').extract_first().strip()
                        item['content'] = news.css('div.nstory_intro::text').extract_first()
                        item['link'] = news.css('div.nstory_header>a::attr(href)').extract_first()
                        item['newsDate'] = self.parse_date(item['link'])
                        #item['source'] = 104
                        self.custom_settings['url_stats']['scraped'] += 1
                        yield item
                    else:
                        logger.debug(__name__+' Skipping a News Item, most probably an Advertisment')
                self.page_counter += 1
                next_page = 'http://www.ndtv.com/latest/page-' + str(self.page_counter)
                yield scrapy.Request(next_page, callback=self.parse)
            except Exception as e:
                logger.error(__name__+" Unhandled: "+str(e))
        else:
            logger.error(__name__ + " Non-200 Response Received : " + response.status + " for url " + response.url)
            return False

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
            logger.critical(__name__+' Error Extracting Date : ' + link)
            return None

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with url stats " + str(self.custom_settings['url_stats']))
