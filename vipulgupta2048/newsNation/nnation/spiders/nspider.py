import scrapy
from nnation.items import NnationItem

class nation(scrapy.Spider):
    name = "nnation"
    start_urls = ['http://www.newsnation.in/business-news',]

    def parse(self,response):
        newsBox = response.xpath('//ul[contains(@class, "ciln")]/li')
        for box in newsBox:
            link = box.xpath('./div[2]/h2/a/@href').extract_first()
            yield response.follow(link, callback = self.parse_article)

        next_page = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_page is not None:
            print("==============Switching Page======================")
            yield response.follow(next_page, callback = self.parse)

    def parse_article(self,response):
        i = NnationItem()
        i['headline'] = response.xpath("//h1/text()").extract_first()
        yield i
        #print (response.xpath('//a').extract())
        #news = response.xpath('//div[@class ="top-news"]//div[contains(@class, "top-story")]').extract()
        #print (news)
        #for article in news:
            #z1 = article.xpath('.//div[@class = "col-sm-4 col-xs-12"]')
            #z2 = article.xpath ('.//div[@class="hede-cate"]')

            #i['link'] = z1.xpath('.//a/@href').extract_first()
            #i['images'] = z1.xpath('.//img/@src').extract_first()
            #i['summary'] = z2.xpath ('//p/text()').extract_first()
            #i['date'] = z2.xpath ('//span[2][contains(@class, "posted")]/text()').extract_first()
            #i['headline'] = z2.xpath('//h3/a/text()').extract_first()
            #yield i 
