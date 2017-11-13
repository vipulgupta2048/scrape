import scrapy
import json
from news18.settings import logger
from news18.items import News18Item

class News18Spider(scrapy.Spider):
    name = "News18Spider"
    
    custom_settings = {
        'site_name': "News18",
        'site_url': "https://www.news18.com",
        'site_id': -1,
        'urls_scraped': []  #Remove incase of OPTION 2 for duplicates handling
    }
    
    start_url = "http://www.news18.com/news/"
    ignoreClasses = ["photoiconb", "photoicons", "vodeoiconb", "vodeoicons"]

    def start_requests(self):
        yield scrapy.Request(url = self.start_url, callback=self.parse)

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__+" [STATUS] "+response.status)
        else:
            news_sections = response.xpath('//div[contains(@class,"blog-list-blog")]')
            for section in news_sections:
                news_type = section.xpath("./a[1]/@class").extract_first()
                if news_type is not None:
                    flag = 0
                    news_type = news_type.split(" ")
                    for x in news_type:
                        if x in self.ignoreClasses:
                            flag = 1 
                            logger.debug(__name__+" [SKIPPED] "+x+" is in Ignored List")
                    if flag:
                        continue

                title = section.xpath("./p/a/text()").extract_first()
                href = response.urljoin(section.xpath("./p/a[1]/@href").extract_first())
                # Choice 1 (List Method)
                if href not in self.custom_settings['urls_scraped']:
                    yield scrapy.Request(url = href, callback=self.parse_news)
                """
                # Choice 2 (DATABASE Method)
                if not NewsDatabase().urlExists(href):
                    yield scrapy.Request(url = href, callback=self.parse_news)
                
                # Choice 3 (Do Nothing, Let Pipeline Handle the duplicates)
                yield scrapy.Request(url = href, callback=self.parse_news)
                """
            next_page = response.xpath('//div[contains(@class, "pagination")]/ul/li[contains(@class,"next")]/a/@href').extract_first();
            if next_page is not None:
                logger.info(__name__+" Moving to Next Page")
                yield scrapy.Request(url = response.urljoin(next_page))
        yield {"status": "Completed"}
    
    def parse_news(self, response):
        news_url = news_title = news_description = news_picture = ""
        try:
            news_url = response.url
            news_title = response.xpath("//h1/text()").extract_first()
            news_description = response.xpath("//div[@id='article_body']/text()").extract_first()
            news_picture = response.xpath("//div[contains(@class, 'articleimg')]/picture/source[1]/@srcset").extract_first()
            item = News18Item({'url': news_url, 'title': news_title, 'description': news_description, 'image': news_picture})
            yield item
        except Exception as e:
            logger.error(__name__+" Error in xpath: "+str(e))