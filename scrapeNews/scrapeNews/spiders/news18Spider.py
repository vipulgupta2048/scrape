import scrapy
import re
from scrapeNews.settings import logger
from scrapeNews.items import ScrapenewsItem
from scrapeNews.db import DatabaseManager, LogsManager

class News18Spider(scrapy.Spider):
    name = "News18Spider"

    custom_settings = {
        'site_name': "News18",
        'site_url': "https://www.news18.com",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
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

    def closed(self, reason):
        self.postgres.closeConnection(reason)


    def start_requests(self):
        yield scrapy.Request(url = self.start_url, callback=self.parse)

    def log_ip(self, response):
        ip = response.xpath("//body/text()").extract_first()
        logger.debug(__name__+" "+ip)
        yield None

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__+" HTTP ERROR "+response.status)
            yield None
        else:
            # yield scrapy.Request(url="http://checkip.dyndns.org/", callback=self.log_ip) # Logs IP (for tor use) (Experiment)
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

                if not DatabaseManager().urlExists(href):
                    self.custom_settings['url_stats']['parsed'] += 1
                    yield scrapy.Request(url = href, callback=self.parse_news) #Let Pipeline Handle duplicates (Consumes more bandwidth)
                else:
                    self.custom_settings['url_stats']['dropped'] += 1

            next_page = response.xpath('//div[contains(@class, "pagination")]/ul/li[contains(@class,"next")]/a/@href').extract_first();
            if next_page is not None:
                logger.debug(__name__+" Moving to Next Page")
                yield scrapy.Request(url = response.urljoin(next_page))

    def parse_news(self, response):

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
            self.custom_settings['url_stats']['dropped'] += 1    
            yield None
            return
        elif len(news_picture) == 0 or len(news_description) == 0 or len(news_picture) == 0 or len(news_date) == 0:
            logger.error(__name__+" Empty Data for URL "+news_url)
            self.custom_settings['url_stats']['dropped'] += 1
            yield None
            return
        
        item = ScrapenewsItem({'link': news_url, 'title': news_title, 'content': news_description, 'image': news_picture, 'newsDate': news_date})

        self.custom_settings['url_stats']['scraped'] += 1
        yield item

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
