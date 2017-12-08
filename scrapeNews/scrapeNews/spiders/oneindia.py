# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from scrapeNews.db import DatabaseManager, LogsManager

class OneindiaSpider(scrapy.Spider):

    name = 'oneindia'
    allowed_domains = ['oneindia.com']

    custom_settings = {
        'site_name': "oneindia",
        'site_url': "https://www.oneindia.com/india/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "https://www.oneindia.com/india/?page-no="
    #def __init__(self, offset=0, pages=2, *args, **kwargs):
        #self.postgres = pipeline()
        #self.postgres.openConnection()
    #    super(OneindiaSpider, self).__init__(*args, **kwargs)
    #    for count in range(int(offset), int(offset) + int(pages)):
    #        self.start_urls.append('https://www.oneindia.com/india/?page-no='+ str(count+1))

    #@classmethod
    #def from_crawler(cls, crawler, *args, **kwargs):
    #    spider = super(OneindiaSpider, cls).from_crawler(crawler, *args, **kwargs)
    #    crawler.signals.connect(spider.spider_closed, scrapy.signals.spider_closed)
    #    return spider

    #def spider_closed(self, spider):
        #self.postgres.closeConnection()
    #    return True

    def start_requests(self):
        yield scrapy.Request(self.start_url+"1", self.parse)
    #    for url in self.start_urls:
    #        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        try:
            newsContainer = response.xpath('//div[@id="collection-wrapper"]/article')
            for newsBox in newsContainer:
                link = 'https://www.oneindia.com/india/' + newsBox.xpath('div/h2/a/@href').extract_first()
                if not DatabaseManager().urlExists(link):
                    self.custom_settings['url_stats']['parsed'] += 1
                    yield scrapy.Request(url=link, callback=self.parse_article)
                else:
                    self.custom_settings['url_stats']['dropped'] += 1
            try:
                next_page = response.urljoin(response.xpath("//div[contains(@class, 'prev-next-story')]//a[contains(@class, 'next')]/@href").extract_first())
                yield scrapy.Request(next_page, self.parse)
            except Exception as e:
                #Scraping Completed
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
        #item['source'] = 109
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None


    def getPageContent(self, response):
        try:
            data = ' '.join((''.join(response.xpath("//div[contains(@class,'io-article-body')]/p/text()").extract())).split(' ')[:40])
        except Exception as Error:
            logger.error(__name__ + " Error Extracting Content : "+ response.url + " : " + str(Error))
            data = 'Error'
        return data

    def getPageTitle(self, response):
        data = response.xpath("//h1[contains(@class,'heading')]/text()").extract_first()
        if (data is None):
            logger.error(__name__ + "Error Extracting Title: " + response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = 'https://www.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@data-pagespeed-lazy-src").extract_first()
        if (data is None):
            logger.error(__name__ + " Error Extracting Image: " + response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            data = (response.xpath("/html/head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__ + " Error Extracting Date: " + response.url + " : " + str(Error))
            data = 'Error'
        finally:
            return data

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
