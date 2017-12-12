# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import LogsManager, DatabaseManager

class AsianageSpider(scrapy.Spider):

    custom_settings = {
        'site_name': "asianage",
        'site_url': "http://www.asianage.com/newsmakers",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    name = 'asianage'
    allowed_domains = ['asianage.com']
    start_url = 'http://www.asianage.com/newsmakers?pg='


    def start_requests(self):
        yield scrapy.Request(self.start_url+str(1), self.parse)


    def parse(self, response):
        try:
            newsContainer = response.xpath("//div[contains(@class,'india-news')]/div[@class='singlesunday']")
            for newsBox in newsContainer:
                self.custom_settings['url_stats']['parsed'] += 1
                item = ScrapenewsItem()  # Scraper Items
                item['image'] = self.getPageImage(newsBox)
                item['title'] = self.getPageTitle(newsBox)
                item['content'] = self.getPageContent(newsBox)
                item['newsDate'] = self.getPageDate(newsBox)
                item['link'] = self.getPageLink(newsBox)

                if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                    self.custom_settings['url_stats']['scraped'] += 1
                    yield item
                else:
                    self.custom_settings['url_stats']['dropped'] += 1
                    yield None
            next_page_link = response.xpath("//div[contains(@class,'pagingBlock')]/ul/li/a/@href").extract()[-1]
            if next_page_link != "#":
                next_page = response.urljoin(next_page_link)
                yield scrapy.Request(next_page, self.parse)
        except Exception as e:
            logger.error(__name__+" Unhandled: "+str(e))

    def getPageContent(self, newsBox):
        data = newsBox.xpath('div/p[@class="These"]/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to extract Content " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageTitle(self, newsBox):
        data = newsBox.xpath('div/h2/a/text()').extract_first()
        if (data is None):
            logge.error(__name__ + " Unable to extract Title: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageLink(self, newsBox):
        data = 'http://www.asianage.com/newsmakers' + newsBox.xpath('div/a/@href').extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to extract Link: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageImage(self, newsBox):
        data = newsBox.xpath('div/a/img/@data-src').extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to extract URL: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def getPageDate(self, newsBox):
        data = newsBox.xpath('div/p[@class="newDate"]/text()').extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to extract Date: " + str(newsBox.extract_first()))
            data = 'Error'
        return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to End Log for Spider " + self.name + " with stats: " + str(self.custom_settings['url_stats']))
