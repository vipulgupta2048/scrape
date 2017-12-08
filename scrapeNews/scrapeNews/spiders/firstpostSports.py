# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import DatabaseManager, LogsManager

class FirstpostsportsSpider(scrapy.Spider):

    name = 'firstpostSports'
    allowed_domains = ['firstpost.com']

    custom_settings = {
        'site_name': "firstpost(sports)",
        'site_url': "http://www.firstpost.com/category/sports/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "http://www.firstpost.com/category/sports/page/1"
    #def __init__(self, offset=0, pages=3, *args, **kwargs):
        #self.postgres = pipeline()
        #self.postgres.openConnection()
    #    super(FirstpostsportsSpider, self).__init__(*args, **kwargs)
    #    for count in range(int(offset), int(offset) + int(pages)):
    #        self.start_urls.append('http://www.firstpost.com/category/sports/page/'+ str(count+1))


    #@classmethod
    #def from_crawler(cls, crawler, *args, **kwargs):
    #    spider = super(FirstpostsportsSpider, cls).from_crawler(crawler, *args, **kwargs)
    #    crawler.signals.connect(spider.spider_closed, scrapy.signals.spider_closed)
    #    return spider

    #def spider_closed(self, spider):
    #    #self.postgres.closeConnection()
    #    return True


    def start_requests(self):
        yield scrapy.Request(self.start_url, self.parse)
    #    for url in self.start_urls:
    #        yield scrapy.Request(url, self.parse)


    def parse(self, response):
        try:
            newsContainer = response.xpath("//ul[@class='articles-list']/li")
            for newsBox in newsContainer:
                link = newsBox.xpath('a/@href').extract_first()
                if not DatabaseManager().urlExists(link):
                    self.custom_settings['url_stats']['parsed'] += 1
                    yield scrapy.Request(url=link, callback=self.parse_article)
                else:
                    self.custom_settings['url_stats']['dropped'] += 1
            last_page = response.urljoin(response.xpath("//ul[contains(@class,'pagination')]/li/a/@href").extract()[-1])
            next_page = response.urljoin(response.xpath("//a[@rel='next']/@href").extract_first())
            if next_page != None:
                yield scrapy.Request(next_page, self.parse)
            else:
                if response.url != last_page:
                    next_page = response.urljoin(response.xpath("//ul[contains(@class,'pagination')]/li[@class='active']/following-sibling::li/a/@href").extract_first())
                    if next_page != None:
                       yield scrapy.Request(next_page, self.parse)
        except Exception as e:
            logger.error(__name__+" Unhandled <"+response.url+">: "+str(e))


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        #item['source'] = 112
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None


    def getPageTitle(self, response):
        try:
            data = ' '.join(response.xpath("//h1[@itemprop='headline']/text()").extract_first().split())
        except AttributeError as Error:
            try:
                data = response.xpath('//h1[@class="story-title"]/text()').extract_first()
            except Exception as Error:
                logger.error(__name__+" Error Extracting Title <"+response.url+">: "+str(Error))
                data = 'Error'
        except Exception as Error:
            logger.error(__name__+" Error Extracting Title <"+response.url+">: "+str(Error))
            data = 'Error'
        finally:
            return data

    def getPageImage(self, response):
        data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
        if (data is None):
            logger.error(__name__+" Error Extracting Image <"+response.url+">")
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__+" Error Extracting Date < "+response.url+">: "+str(Error))
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        try:
            data = ' '.join((' '.join(response.xpath("//div[contains(@class,'article-full-content')]/p/text()").extract())).split(' ')[:40])
        except Exception as Error:
            logger.error(__name__+" Error Extracting Content <"+response.url+">: "+str(Error))
            data = 'Error'
        finally:
            return data

    def close(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
