import scrapy
import re
from scrapeNews.settings import logger
from scrapeNews.items import ScrapenewsItem

class News18Spider(scrapy.Spider):
    name = "News18Spider"

    custom_settings = {
        'site_id': 107,
        'site_name': "News18",
        'site_url': "https://www.news18.com",
    }

    xpaths = {
        'default': {
            'title': "//h1/text()",
            'description': "//div[@id='article_body']/text()",
            'image': "//div[contains(@class, 'articleimg')]/picture/source[1]/@srcset",
            'date': "//div[contains(@class, 'author')]/span/text()"
        },
        'cricketnext': {
            'title': "//h1/text()",
            'description': "//article[@class='paragraph']/text()",
            'image': "//figure[@class='article-img']/picture/source[1]/@srcset",
            'date': "//meta[@itemprop='datePublished']/@content"
        },
        'indiwo': {
            'title': "//h1/text()",
            'description': "//div[@class='news-contens']/text()",
            'image': "//div[contains(@class, 'photo-cn')]/img/@src",
            'date': "//div[contains(@class, 'photo-caption')][1]/text()[2]"
        }
    }

    start_url = "http://www.news18.com/news/"
    ignoreClasses = ["photoiconb", "photoicons", "vodeoiconb", "vodeoicons"]

    def start_requests(self):
        yield scrapy.Request(url = self.start_url, callback=self.parse)

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__+" Non-200 Response Received : " + response.status)
            return False
        try:
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

                href = response.urljoin(section.xpath("./p/a[1]/@href").extract_first())

                if not self.postgres.checkUrlExists(href):
                    self.urls_parsed += 1
                    yield scrapy.Request(url = href, callback=self.parse_news)
                else:
                    self.urls_dropped += 1

            next_page = response.xpath('//div[contains(@class, "pagination")]/ul/li[contains(@class,"next")]/a/@href').extract_first();
            if next_page is not None:
                logger.debug(__name__+" Moving to Next Page")
                yield scrapy.Request(url = response.urljoin(next_page))
        except Exception as e:
            logger.error(__name__ + " Unhandled: " + str(e))

    def parse_news(self, response):
        try:
            news_url = response.url
            news_parser = "default"

            for parser_str in self.xpaths:
                match = r'\/'+re.escape(parser_str)+r'\/'
                if re.search(match, news_url) is not None:
                    news_parser = parser_str
                    break

            news_title = response.xpath(self.xpaths[news_parser]['title']).extract_first()
            news_description = response.xpath(self.xpaths[news_parser]['description']).extract_first()
            news_picture = response.xpath(self.xpaths[news_parser]['image']).extract_first()
            news_date = response.xpath(self.xpaths[news_parser]['date']).extract_first()

            if news_title == None or news_description == None or news_picture == None or news_date == None:
                logger.error(__name__+" Error Extracting Data for URL " + news_url)
                self.urls_dropped += 1    
                yield None
                return
            elif len(news_picture) == 0 or len(news_description) == 0 or len(news_picture) == 0 or len(news_date) == 0:
                logger.error(__name__+" Empty Data for URL "+news_url)
                self.urls_dropped += 1
                yield None
                return

            item = ScrapenewsItem({'link': news_url, 'title': news_title, 'content': news_description, 'image': news_picture, 'newsDate': news_date, 'source': self.custom_settings['site_id']})

            self.urls_scraped += 1
            yield item
        except Exception as e:
            logger.error(__name__ + " Unhandled <" + response.url + ">: " + str(e))