import scrapy
from scrapeNews.items import ScrapenewsItem
from scrapeNews.db import LogsManager


class zeespider(scrapy.Spider):
    name = "zee"
    start_urls = ['http://zeenews.india.com/india',]
    custom_settings = {
        'site_id':106,
        'site_name':'Zee News',
        'site_url':'http://zeenews.india.com/india'}


    def closed(self, reason):
        self.postgres.closeConnection(reason)


    custom_settings = {
        'site_name': "Zee News",
        'site_url': "http://zeenews.india.com/india",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    #Scraping the main page for article links
    def parse(self, response):
        articles = response.xpath('//section[contains(@class, "maincontent")]//div[contains(@class, "section-article")]') #extracts HTML from the start_url
        for article in articles:
            x = article.xpath('.//h3/a[2]') #extracts <a> tag from start _url
            link = x.xpath('.//@href').extract_first()  #extracts URL for the articles recursively
            self.custom_settings['url_stats']['parsed'] += 1
            yield response.follow(link, callback = self.parse_news)

        #For scraping the links on the next page of the website
        next_page = response.xpath('//link[@rel = "next"]/@href').extract_first()
        if next_page is not None:
           yield response.follow(next_page, callback = self.parse)

    #For scraping a particular article listed on the main page
    def parse_news(self,response):
        i = ScrapenewsItem()
        i['title'] = response.xpath('//h1[contains(@class, "article-heading margin")]/text()').extract_first() #scrapes headline 
        i['newsDate'] = response.xpath('//span[contains(@class, "date")]/text()').extract_first()[10:-4] #scrapes datetime
        i['image'] = response.xpath('//div[contains(@class, "field-item")]/img/@src').extract_first() #scrapes image url
        i['content'] = self.getcontent(response)
        i['link'] = response.url #scrapes link; article page

        self.custom_settings['url_stats']['scraped'] += 1
        yield i

    def getcontent(self,response):
        data = response.xpath('//div[contains(@class, "article")]/div[contains(@class, "field")]//p/text()').extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data

    def closed(self, reason):
        LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason)
