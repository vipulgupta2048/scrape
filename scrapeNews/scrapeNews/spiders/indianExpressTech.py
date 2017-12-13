# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import DatabaseManager, LogsManager

class IndianexpresstechSpider(scrapy.Spider):

    name = 'indianExpressTech'
    allowed_domains = ['indianexpress.com']

    custom_settings = {
        'site_name': "Indian Express",
        'site_url': "http://indianexpress.com/section/technology/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    base_url = "https://indianexpress.com/section/technology/"
    start_url = base_url+"page/"
    page_count = 1


    def start_requests(self):
        yield scrapy.Request(self.start_url+"1", self.parse)

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__ + " Non-200 Response Received : " + response.status + " for url " + response.url)
            return False
        try:
            if response.url != self.base_url:
                newsContainer = response.xpath('//div[@class="top-article"]/ul[@class="article-list"]/li')
                for newsBox in newsContainer:
                    link = newsBox.xpath('figure/a/@href').extract_first()
                    if not DatabaseManager().urlExists(link):
                        self.custom_settings['url_stats']['parsed'] += 1
                        yield scrapy.Request(url=link, callback=self.parse_article)
                    else:
                        self.custom_settings['url_stats']['dropped'] += 1
                self.page_count += 1
                yield scrapy.Request(self.start_url+str(self.page_count), self.parse)
        except Exception as e:
            logger.error(__name__+" Unhandled: "+str(e))


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url

        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None

    def getPageContent(self, response):
        data = response.xpath('//h2[@class="synopsis"]/text()').extract_first()
        if (data is None):
            data = response.xpath("//div[@class='full-details']/p/text()").extract_first()
        if (data is None):
            data = ' '.join(' '.join(response.xpath("//div[@class='body-article']/p/text()").extract()).split()[:40])
        if not data:
            logger.error(__name__+" Error Extracting Content " + response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Title " + response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath('//span[@class="custom-caption"]/img/@data-lazy-src').extract_first()
        if (data is None):
            data = response.xpath("//span[@itemprop='image']/meta[@itemprop='url']/@content").extract_first()
        if (data is None):
            try:
                data = ((response.xpath('//div[@class="lead-article"]/@style').extract_first()).split('url(',1)[1]).split(')',1)[0]
            except Exception as Error:
                logger.error(__name__+" Error Extracting Image:  " + response.url + " : " +str(Error))
                data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            data = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        except Exception as Error:
            logger.error(__name__+" Error Extracting Date: " + response.url + " : " + str(Error))
            data = 'Error'
        return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with stats " + str(self.custom_settings['url_stats']))
