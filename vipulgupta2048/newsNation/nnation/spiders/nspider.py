import scrapy


class nnation(scrapy.Spider):
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
        i['link'] = response.url 
        i['images'] = response.xpath('//div[contains(@itemprop, "image")]//img/@src').extract_first()
        i['date'] = response.xpath('//span[contains(@itemprop, "date")]/text()').extract_first()
        i['summary'] = response.xpath('//div[@itemprop ="articleBody"]//p/text()').extract()
        
        yield i
