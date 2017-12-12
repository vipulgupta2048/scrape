# -*- coding: utf-8 -*-
import scrapy


class HindustanSpider(scrapy.Spider):
    name = 'hindustan'
    allowed_domains = ['www.hindustantimes.com']
    temp = 'http://www.hindustantimes.com/Fragment/HT/Web/Components/home-editors-pick.dwc?style=/PortalConfig/www.ns.hindustantimes.com/jpt-ns/include/fragments/show-more-fragment.jpt&offset='
    start_urls = [temp+'1']
    count = 1
    def parse(self, response):
        something = response.css('div.media')
        for somethings in something:
            link = somethings.xpath('.//div[contains(@class,"media-body")]/div[1]/a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.fun)
        self.count += 1
        
        yield scrapy.Request(url=self.temp+str(self.count), callback=self.parse)


    def fun(self, response):
        text = response.text
        text = response.text
        headline = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        images = response.xpath('//div[@class="thumbnail"]/img/@src').extract_first()
        body = response.xpath('//div[@itemprop="articlebody"]/p').extract_first()
        date = response.css('span.text-dt::text').extract_first()
        date = date.replace('Updated:',"")
        item = {'title': headline, 'link': response.url, 'date': date, 'content': body, 'image': images}
        yield item

    


            