import scrapy

class Dnaindia(scrapy.Spider):
    name = 'dnaindia'
    allowed_domains = ['http://www.dnaindia.com']
    temp = 'http://www.dnaindia.com/technology?page='
    start_urls = [temp+'1']
    count = 1
    def parse(self, response):
        something = response.css('div.bolyveralign')
        for somethings in something:
            link = somethings.css('//*[@id="block-views-daff1426d5cfb9d13a9d770f023dde8c"]/div/div/div/div[1]/div/div[2]/h3/a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.fun)
        self.count +=1
        yield scrapy.Request(url=self.temp+str(self.count), callback=self.parse)

    def fun(self, response):
        text = reponse.text
        headline = response.xpath('//*[@id="block-system-main"]/div/div/section/div/div/h1/text()').extract_first()
        images = response.xpath('//*[@id="block-system-main"]/div/div/section/div/div/img').extract_first()
        body = response.xpath('//*[@id="block-system-main"]/div/div/section/div/div/div[1]/div/div[2]/p[1]/text()').extract_first()
        date = response.xpath('//*[@id="block-system-main"]/div/div/section/div/div/div[1]/div/div[1]/div[3]/date').extract_first()

        item = {'title': headline, 'link': response.url, 'date': date, 'content': body, 'image': images}
        yield item
         
