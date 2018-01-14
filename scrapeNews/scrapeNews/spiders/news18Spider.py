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
            logger.error(__name__ + " [UNHANDLED] " + str(e) + " for response url " + response.url)

    def parse_news(self, response):
        try:
            item = ScrapenewsItem()

            item['link'] = response.url
            item['source'] = self.custom_settings['site_id']
            news_parser = "default"

            for parser_str in self.xpaths:
                match = r'\/'+re.escape(parser_str)+r'\/'
                if re.search(match, item['link']) is not None:
                    news_parser = parser_str
                    break

            logger.debug(__name__ + " Using " + news_parser + " parser for url " + response.url)

            item['title'] = response.xpath(self.xpaths[news_parser]['title']).extract_first()
            item['content'] = response.xpath(self.xpaths[news_parser]['description']).extract()[0]
            item['image'] = response.xpath(self.xpaths[news_parser]['image']).extract_first()
            item['newsDate'] = response.xpath(self.xpaths[news_parser]['date']).extract_first()
            
            # Remove Escaped Characters
            item['content'] = re.sub(r"[\t\r\n]{0,}", "", item['content'])

            # Remove Unwanted Spaces from start and end
            item['content'] = re.sub(r"^\s{0,}|\s{0,}$", "", item['content'])

            for key in item:
                if item[key] == None and key != 'image':
                    logger.error(__name__ + " A Required Key wasn't extracted: " + key)
                    self.urls_dropped += 1
                    yield None

            yield item
            self.urls_scraped += 1

        except Exception as e:
            logger.error(__name__ + " [UNHANDLED] : " + str(e) + " for response url " + response.url)
            self.urls_dropped += 1