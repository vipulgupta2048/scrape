import scrapy
from news.items import NewsItem

class newsspider(scrapy.Spider):
     name='news'
     allowed_domain = ['http://www.greatplantpicks.org/plantlists']
     start_urls = ['http://www.greatplantpicks.org/plantlists/by_plant_type/conifer']
     #clones the repo
     #def parse(self , response):
         #filename = response.url.split("/")[-2] + '.html'
         #with open(filename, 'wb') as f:
             #f.write(response.body)

     def parse(self , response):
         for sel in response.xpath('//tbody/tr'): #select rows
              item = NewsItem()
              item['name'] = sel.xpath('.//td[@class="common-name"]/a/text()').extract_first()
              item['genus'] = sel.xpath('.//td[@class="plantname"]/a/span[@class="genus"]/text()').extract_first()
              item['species'] = sel.xpath('.//td[@class="plantname"]/a/span[@class="species"]/text()').extract_first()
              yield item
