# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


class FirstposthindiSpider(scrapy.Spider):

    name = 'firstpostHindi'
    allowed_domains = ['hindi.firstpost.com']
    custom_settings = {
        'site_id':111,
        'site_name':'firstpost(hindi)',
        'site_url':'https://hindi.firstpost.com/category/latest/'}


    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(FirstposthindiSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('https://hindi.firstpost.com/category/latest/page-'+ str(count+1))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        newsContainer = response.xpath("//ul[@id='more_author_story']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('h2/a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article)


    def parse_article(self, response):
        if (str(response.url) != "https://hindi.firstpost.com/") and (not response.xpath("//div[@id='play_home_video']") and (not response.xpath('//div[contains(@class,"pht-artcl-top")]'))):
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 111
            if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
                yield item


    def getPageTitle(self, response):
        data = response.xpath("//h1[@class='hd60']/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = ' '.join((' '.join(response.xpath("//div[contains(@class,'csmpn')]/p/text()").extract())).split(' ')[:40])
        if not data:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        return data
