import scrapy

class nation(scrapy.Spider):
    name = "nnation"
    start_urls = ['http://www.newsnation.in/business-news',]
    
    def parse(self,response):
        links = response.xpath('//div[@class= "col-sm-8"]/h2/a[@href]')
        for link in links:
            x = link.xpath('.//@href').extract_first()
            yield response.follow(x, callback = self.parse_article)
            
    def parse_article(self,response):
        news = response.xpath('//div[@class ="top-news"]//div[contains(@class, "top")]').extract()
        print (news)
        for article in news:      
            x = article.xpath('//div[@class="hede-cate"]')
            y = x.xpath('/h3/a[@href]')
            print (y)

            
