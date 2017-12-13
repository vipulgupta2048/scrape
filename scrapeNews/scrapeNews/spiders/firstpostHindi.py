# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import DatabaseManager, LogsManager

class FirstposthindiSpider(scrapy.Spider):

    name = 'firstpostHindi'
    custom_settings = {
        'site_id':111,
        'site_name':'firstpost(hindi)',
        'site_url':'https://hindi.firstpost.com/category/latest/'}

    custom_settings = {
        'site_name': "firstpost(hindi)",
        'site_url': "https://hindi.firstpost.com/category/latest/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "https://hindi.firstpost.com/category/latest/page-1/"

    def start_requests(self):
        yield scrapy.Request(self.start_url, self.parse)

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__ + " Non-200 Response Received : " + response.status + " for url " + response.url)
        newsContainer = response.xpath("//ul[@id='more_author_story']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('h2/a/@href').extract_first()
            if not DatabaseManager().urlExists(link):
                self.custom_settings['url_stats']['parsed'] += 1
                yield scrapy.Request(url=link, callback=self.parse_article)
            else:
                self.custom_settings['url_stats']['dropped'] += 1
        last_page = response.urljoin(response.xpath("//div[@class='pagination']/ul/li/a/@href").extract()[-1])
        next_page = response.urljoin(response.xpath("//div[@class='pagination']/ul/li[@class='active']/following-sibling::li/a/@href").extract_first())
        if last_page != response.url:
            yield scrapy.Request(next_page, self.parse)

    def parse_article(self, response):
        if ((str(response.url) != "https://hindi.firstpost.com/") and ((not response.xpath("//div[@id='play_home_video']")) and (not response.xpath('//div[contains(@class,"pht-artcl-top")]')) and (not self.postgres.checkUrlExists(response.url)))):
            self.urls_parsed -= 1
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url

            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                self.custom_settings['url_stats']['scraped'] += 1
                yield item
            else:
                self.custom_settings['url_stats']['dropped'] += 1
                yield None
        else:
            self.custom_settings['url_stats']['dropped'] += 1


    def getPageTitle(self, response):
        data = response.xpath("//h1[@class='hd60']/text()").extract_first()
        if (data is None):
            logger.error(__name__+" Unable to Extract Title: "+response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
        if (data is None):
            logger.error(__name__+" Unable to Extract Image: "+response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__+" Unhandled: "+str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        try:
            data = ' '.join((' '.join(response.xpath("//div[contains(@class,'csmpn')]/p//text()").extract())).split(' ')[:40])
            if not data:
                    data = ' '.join((' '.join(response.xpath("//div[contains(@class,'aXjCH')]/div/p//text()").extract())).split(' ')[:40])
                    if not data:
                        data = ' '.join((' '.join(response.xpath("//div[contains(@class,'csmpn')]/div/p/text()").extract())).split(' ')[:40])
                        if not data:		
                            data = response.xpath("//div[@class='fulstorysharecomment']/text()").extract_first()		
                            if not data:		
                                data =  ' '.join((' '.join(response.xpath("//div[@class='fullstorydivstorycomment']/p/text()").extract())).split(' ')[:40])		
                                if not data:		
                                    data = ' '.join((' '.join(response.xpath("//div[contains(@class,'csmpn')]/div[not(@class)]/text()").extract())).split(' ')[:40])		
                                    if not data:		
                                        logger.error(__name__ + " Unable to Extract Content for url : " + response.url)
                                        data = 'Error'
                                        return data
        except Exception as e:
            logger.error(__name__ + " Unhandled: " + str(e))
            return "Error"

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)