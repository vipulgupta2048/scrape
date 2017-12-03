# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError
from scrapeNews.db import DatabaseManager, LogsManager

class NewsxSpider(scrapy.Spider):

    name = 'newsx'
    allowed_domains = ['newsx.com']
    start_urls = ['http://newsx.com/']

    custom_settings = {
        'site_name': "newsx",
        'site_url': "http://www.newsx.com/latest-news/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    def __init__(self, offset=0, pages=4, *args, **kwargs):
        #self.postgres = pipeline()
        #self.postgres.openConnection()
        super(NewsxSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('http://www.newsx.com/latest-news/page/'+ str(count+1))


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NewsxSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        #self.postgres.closeConnection()
        return True


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)
            sleep(1)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        newsContainer = response.xpath("//div[contains(@class,'cat-grid-gap')]/div[@class='well ft2']")
        for newsBox in newsContainer:
            link = newsBox.xpath('div/a/@href').extract_first()
            if not DatabaseManager().urlExists(link):
                self.custom_settings['url_stats']['parsed'] += 1
                yield scrapy.Request(url=link, callback=self.parse_article)
            else:
                self.custom_settings['url_stats']['dropped'] += 1


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        #item['source'] = 113
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None


    def getPageTitle(self, response):
        try:
            data = ' '.join(response.xpath("//h1[@itemprop='headline']/text()").extract_first().split())
        except Exception as Error:
            loggerError.error(str(Error) +" occured at: "+ response.url)
            data = 'Error'
        finally:
            return data

    def getPageImage(self, response):
        data = response.xpath("//head/link[@rel='image_src']/@href").extract_first()
        if (data is None):
            data = response.xpath("//div[@class='panel-body story']/div[@class='thumbnail video-thumbnail']/img/@src").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@itemprop='datePublished']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(str(Error) +" occured at: "+ response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = response.xpath("//div[@class='story-short-title']/h2/text()").extract_first()
        if (data is None):
            data = ' '.join(' '.join(response.xpath("//div[@itemprop='articleBody']/p/text()").extract()).split()[:40])
        if not data:
            loggerError.error(response.url)
            data = 'Error'
        return data

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
