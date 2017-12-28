# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.pipelines import loggerError


class FirstposthindiSpider(scrapy.Spider):

    name = 'firstpostHindi'
    custom_settings = {
        'site_id':111,
        'site_name':'firstpost(hindi)',
        'site_url':'https://hindi.firstpost.com/category/latest/'}


    def __init__(self, offset=0, pages=3, *args, **kwargs):
        super(FirstposthindiSpider, self).__init__(*args, **kwargs)
        for count in range(int(offset), int(offset) + int(pages)):
            self.start_urls.append('https://hindi.firstpost.com/category/latest/page-'+ str(count+1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errorRequestHandler)

    def errorRequestHandler(self, failure):
        self.urls_parsed -= 1
        loggerError.error('Non-200 response at ' + str(failure.request.url))


    def parse(self, response):
        newsContainer = response.xpath("//ul[@id='more_author_story']/li")
        for newsBox in newsContainer:
            link = newsBox.xpath('h2/a/@href').extract_first()
            if not self.postgres.checkUrlExists(link):
                yield scrapy.Request(url=link, callback=self.parse_article, errback=self.errorRequestHandler)



    def parse_article(self, response):
        if ((str(response.url) != "https://hindi.firstpost.com/") and ((not response.xpath("//div[@id='play_home_video']")) and (not response.xpath('//div[contains(@class,"pht-artcl-top")]')) and (not self.postgres.checkUrlExists(response.url)))):
            self.urls_parsed -= 1
            item = ScrapenewsItem()  # Scraper Items
            item['image'] = self.getPageImage(response)
            item['title'] = self.getPageTitle(response)
            item['content'] = self.getPageContent(response)
            item['newsDate'] = self.getPageDate(response)
            item['link'] = response.url
            item['source'] = 111
            if item['title'] is not 'Error' and item['content'] is not 'Error' and item['link'] is not 'Error' and item['newsDate'] is not 'Error':
                self.urls_scraped += 1
                yield item
        else:
            self.urls_parsed -= 1
            yield None


    def getPageTitle(self, response):
        data = response.xpath("//h1[@class='hd60']/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageImage(self, response):
        data = response.xpath("/html/head/meta[@property='og:image']/@content").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def getPageDate(self, response):
        try:
            # split & rsplit Used to Spit Data in Correct format!
            data = (response.xpath("//head/meta[@property='article:published_time']/@content").extract_first()).rsplit('+',1)[0]
        except Exception as Error:
            loggerError.error(str(Error) + ' occured at: ' + response.url)
            data = 'Error'
        finally:
            return data

    def getPageContent(self, response):
        data = ' '.join(response.xpath("//div[contains(@class,'csmpn')]/p//text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[contains(@class,'aXjCH')]/div/p//text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[contains(@class,'csmpn')]/div[not(@class) or @class='alltake_head']//text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[@itemprop='articleBody']/p/text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[@class='fulstorysharecomment']/text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[contains(@class,'csmpn')]/ul/li/text()").extract())
        if not data:
            data =  ' '.join(response.xpath("//div[@class='fullstorydivstorycomment' or @class='fullstorydivstory' or @class='fulstorytext']//text()").extract())
        if not data:
            data =  ' '.join(response.xpath("//div[@class='_1mf _1mj' or @class='ttl']//text()").extract())
        if not data:
            data =  ' '.join(response.xpath("//p[@class='news-intro']//text()").extract())
        if not data:
            data = ' '.join(response.xpath("//div[contains(@class,'csmpn')]/div[not(@class)]/text()").extract())
        if not data:
            loggerError.error(response.url)
            data = 'Error'
        return data
