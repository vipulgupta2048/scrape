# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger


class OneindiahindiSpider(scrapy.Spider):

    name = 'oneindiaHindi'
    allowed_domains = ['oneindia.com']
    custom_settings = {
        'site_id':110,
        'site_name':'oneindia(hindi)',
        'site_url':'https://hindi.oneindia.com/news/india/'}


    def __init__(self, offset=0, pages=4, *args, **kwargs):
        super(OneindiahindiSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('https://hindi.oneindia.com/news/india/?page-no='+ str(count+1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        logger.error(__name__ + ' Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        try:
            newsContainer = response.xpath('//div[@id="collection-wrapper"]/article')
            for newsBox in newsContainer:
                link = 'https://hindi.oneindia.com' + newsBox.xpath('div/h2/a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)
                    self.urls_parsed += 1
                else:
                    self.urls_dropped += 1
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def parse_article(self, response):
        try:
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 110
            if item['title'] is not 'Error' and item['content'] is not 'Error' and item['newsDate'] is not 'Error':
                self.urls_scraped += 1
                yield item
            else:
                self.urls_dropped += 1
                yield None
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)
            self.urls_dropped += 1


    def getPageContent(self, response):
        try:
            data = ' '.join(response.xpath("//div[contains(@class,'io-article-body')]//text()").extract())
            if not data:
                data = ' '.join(response.xpath("//div[contains(@id,'slider0')]/p/text()").extract())
            if not data:
                data = response.xpath("//article//*[not(self::script) and not(self::style)]/text()").extract()
                data = ' '.join([x for x in data if x != ' ' and x!=u'\xa0']) # Removing all the blank spaces & joining list
            if not data:
                logger.error(__name__ + " Unable to extract Content : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Content : " + str(e) + " : " + response.url)
            data = 'Error'
        return data

    def getPageTitle(self, response):
        try:
            data = response.xpath("//h1[contains(@class,'heading')]/text()").extract_first()
            if (data is None):
                logger.error(__name__ + " Unable to Extract Title : " + response.url)
                data = 'Error'
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] Unable to Extract Title : " + str(e) + " : " + response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        try:
            data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@data-pagespeed-lazy-src").extract_first()
        except Exception as Error:
                data = response.xpath("//link[@rel='image_src']/@href").extract_first()
                if not data:
                    try:
                        data = 'https://hindi.oneindia.com' + response.xpath("//img[contains(@class,'image_listical')]/@src").extract_first()
                    except Exception as Error:
                        logger.error(__name__ + " [UNHANDLED] Unable to Extract Image : " + str(Error) + ' : '+ response.url)
                        data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            data = (response.xpath("//time/@datetime").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            logger.error(__name__ + " [UNHANDLED] Unable to extract Date : " + str(Error) + ' : ' + response.url)
            data = 'Error'
        return data