# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger

class HindustanSpider(scrapy.Spider):

    name = 'hindustan'
    allowed_domains = ['www.hindustantimes.com']
    custom_settings = {
        'site_id':114,
        'site_name':'hindustantimes',
        'site_url':'http://www.hindustantimes.com/editors-pick/'
    }

    temp = 'http://www.hindustantimes.com/Fragment/HT/Web/Components/home-editors-pick.dwc?style=/PortalConfig/www.ns.hindustantimes.com/jpt-ns/include/fragments/show-more-fragment.jpt&offset='
    start_urls = [temp+'1']
    count = 1
    def parse(self, response):
        try:
            something = response.css('div.media')
            for somethings in something:
                link = somethings.xpath('.//div[contains(@class,"media-body")]/div[1]/a/@href').extract_first()
                if not self.postgres.checkUrlExists(link):
                    self.urls_parsed += 1
                    yield scrapy.Request(url=link, callback=self.fun)
                else:
                    self.urls_dropped += 1

            self.count += 1
            yield scrapy.Request(url=self.temp+str(self.count), callback=self.parse)
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url )

    def fun(self, response):
        try:

            text = response.text
            headline = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
            images = response.xpath('//div[@class="thumbnail"]/img/@src').extract_first()
            body = response.xpath('//div[@itemprop="articlebody"]/p').extract_first()
            date = response.css('span.text-dt::text').extract_first()

            item = ScrapenewsItem({'title': headline, 'link': response.url, 'newsDate': date, 'content': body, 'image': images,  'source': 114 })
            self.urls_scraped += 1
            yield item
        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)
