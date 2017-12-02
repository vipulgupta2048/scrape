import scrapy
from scrapeNews.items import ScrapenewsItem



class zeespider(scrapy.Spider):
    name = "zee"
    start_urls = ['http://zeenews.india.com/india',]
    custom_settings = {
        'site_id':106,
        'site_name':'Zee News',
        'site_url':'http://zeenews.india.com/india'}


    #Scraping the main page for article links
    def parse(self, response):
        articles = response.xpath('//section[contains(@class, "maincontent")]//div[contains(@class, "section-article")]') #extracts HTML from the start_url
        for article in articles:
            x = article.xpath('.//h3/a[2]') #extracts <a> tag from start _url
            link = x.xpath('.//@href').extract_first()  #extracts URL for the articles recursively
            yield response.follow(link, callback = self.parse_news)

        #For scraping the links on the next page of the website
        next_page = response.xpath('//link[@rel = "next"]/@href').extract_first()
        if next_page is not None:
           yield response.follow(next_page, callback = self.parse)

    #For scraping a particular article listed on the main page
    def parse_news(self,response):
<<<<<<< HEAD
        i = ScrapenewsItem()
        i['title'] = response.xpath('//h1[contains(@class, "article-heading margin")]/text()').extract_first() #scrapes headline
        i['newsDate'] = response.xpath('//span[contains(@class, "date")]/text()').extract_first()[10:-4] #scrapes datetime
        i['image'] = response.xpath('//div[contains(@class, "field-item")]/img/@src').extract_first() #scrapes image url
        i['content'] = self.getcontent(response)
        i['link'] = response.url #scrapes link; article page
        i['source'] = 106

=======
        i = ScrapenewsItem()                                                       
        i['title'] = response.xpath('//h1[contains(@class, "article-heading margin")]/text()').extract_first() #scrapes headline 
        i['newsDate'] = response.xpath('//span[contains(@class, "date")]/text()').extract_first()[10:-4] #scrapes datetime
        i['image'] = response.xpath('//div[contains(@class, "field-item")]/img/@src').extract_first() #scrapes image url 
        i['content'] = self.getcontent(response)
        i['link'] = response.url #scrapes link; article page
        i['source'] = 106
    
>>>>>>> abe675b... zeenews spider: upgraded: scrapes all news
        yield i

    def getcontent(self,response):
        data = response.xpath('//div[contains(@class, "article")]/div[contains(@class, "field")]//p/text()').extract()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
<<<<<<< HEAD
        return data
=======
        return data 
>>>>>>> abe675b... zeenews spider: upgraded: scrapes all news
