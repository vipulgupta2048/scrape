# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import DatabaseManager, LogsManager

class OneindiahindiSpider(scrapy.Spider):

    name = 'oneindiaHindi'
    allowed_domains = ['oneindia.com']

    custom_settings = {
        'site_name': "oneindia(hindi)",
        'site_url': "https://hindi.oneindia.com/news/india/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "https://hindi.oneindia.com/news/india/?page-no=1"

    def start_requests(self):
        yield scrapy.Request(self.start_url, self.parse)

    def parse(self, response):
        try:
            newsContainer = response.xpath('//div[@id="collection-wrapper"]/article')
            for newsBox in newsContainer:
                link = 'https://hindi.oneindia.com/news/india/' + newsBox.xpath('div/h2/a/@href').extract_first()
                if not DatabaseManager().urlExists(link):
                    self.custom_settings['url_stats']['parsed'] += 1
                    yield scrapy.Request(url=link, callback=self.parse_article)
                else:
                    self.custom_settings['url_stats']['dropped'] += 1
            try:
               next_page = response.urljoin(response.xpath("//div[contains(@class, 'prev-next-story')]//a[contains(@class,'next')]/@href").extract_first())
               if len(next_page) > 0 :
                   yield scrapy.Request(next_page, self.parse)
            except Exception as e:
               # End of Scraping
               return False
        except Exception as e:
            logger.error(__name__ + " Unhandled: " + str(e))

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
        try:
            data = ' '.join((''.join(response.xpath("//div[contains(@class,'io-article-body')]/p/text()").extract())).split(' ')[:40])
            if not data:
                logger.error(__name__ + " Error Extracting Content : " + response.url)
                data = 'Error'    
        except Exception as e:
            logger.error(__name__ + " Error Extracting Content : " + response.url + " :: " + str(e))
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath("//h1[contains(@class,'heading')]/text()").extract_first()
        if (data is None):
            logger.error(__name__+ " Error Extracting Title: " + response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        try:
            data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@src").extract_first()
        except Exception as Error:
            try:
                data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@data-pagespeed-lazy-src").extract_first()
            except Exception as Error:
                data = response.xpath("//link[@rel='image_src']/@href").extract_first()
                if not data:
                    logger.error(__name__ + " Error Extracting Image: " + response.url + " :: " + str(Error))
                    data = 'Error'
            return data

    def getPageDate(self, response):
        try:
            data = (response.xpath("//time/@datetime").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__ + " Error Extracting Date: " + response.url + " : " + str(Error))
            data = 'Error'
        finally:
            return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with stats " + str(self.custom_settings['url_stats']))
