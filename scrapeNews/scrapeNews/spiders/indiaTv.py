# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings  import logger
from scrapeNews.db import DatabaseManager, LogsManager

class IndiatvSpider(scrapy.Spider):

    name = 'indiaTv'
    allowed_domains = ['www.indiatvnews.com']

    custom_settings = {
        'site_name': "India TV",
        'site_url': "http://www.indiatvnews.com/business/tech/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = 'http://www.indiatvnews.com/india/'
    page_count = 1

    def start_requests(self):
        yield scrapy.Request(self.start_url+"1", self.parse)

    def parse(self, response):
        try:
            if response.url != self.start_url:
                newsContainer = response.xpath("//ul[@class='newsListfull']/li")
                for newsBox in newsContainer:
                    link = newsBox.xpath('a/@href').extract_first()
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
        #item['source'] = 102
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None


    def getPageTitle(self, response):
        data = response.xpath('//h1[@class="arttitle"]/text()').extract_first()
        if (data is None):
            logger.error(__name__+" Error Extracting Title: "+response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath('//div[@class="content"]/div/figure/img/@src').extract_first()
        if (data is None):
            logger.error(__name__+" Error Extracting Image: "+response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = response.xpath("//span[@class='dattime']/text()").extract()[1].rsplit(' ', 3)[0]
        except Exception as Error:
            logger.error(__name__+" Error Extracting Date: "+response.url+" : "+str(Error))
            data = 'Error'
        finally:
            return data


    def getPageContent(self, response):
        try:
            data = ' '.join((' '.join(response.xpath("//div[@class='content']/p/text()").extract())).split(' ')[:40])
        except Exception as Error:
            logger.error(__name__+" Error Extracting Content: "+response.url+" : "+str(Error))
            data = 'Error'
        finally:
            return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with stats " + str(self.custom_settings['url_stats']))
