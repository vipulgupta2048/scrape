# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from scrapeNews.db import DatabaseManager, LogsManager

class IndiatvSpider(scrapy.Spider):

    name = 'indiaTv'
    custom_settings = {
        'site_id':102,
        'site_name':'India TV',
        'site_url':'http://www.indiatvnews.com/india/'}

    custom_settings = {
        'site_name': "India TV",
        'site_url': "http://www.indiatvnews.com/business/tech/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = 'http://www.indiatvnews.com/india/'
    page_count = 1
    #def __init__(self, offset=0, pages=3, *args, **kwargs):
        #self.postgres = pipeline()
        #self.postgres.openConnection()
    #    super(IndiatvSpider, self).__init__(*args, **kwargs)
    #    for count in range(int(offset), int(offset) + int(pages)):
    #        self.start_urls.append('http://www.indiatvnews.com/india/' + str(count + 1))

    def closed(self, reason):
        self.postgres.closeConnection(reason)

    def start_requests(self):
        yield scrapy.Request(self.start_url+"1", self.parse)
    #    for url in self.start_urls:
    #        yield scrapy.Request(url, self.parse)


    #@classmethod
    #def from_crawler(cls, crawler, *args, **kwargs):
    #    spider = super(IndiatvSpider,cls).from_crawler(crawler,*args,**kwargs)
    #    crawler.signals.connect(spider.spider_closed,scrapy.signals.spider_closed)
    #    return spider

   # def spider_closed(self, spider):
        #self.postgres.closeConnection()
   #     return True

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
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
