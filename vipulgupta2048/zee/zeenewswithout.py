import json
import requests
from lxml import html

def scrape():
    response = html.fromstring(request.get('http://zeenews.india.com/india').text)
    print(response)
    articles = response.xpath('//section[contains(@class, "maincontent")]//div[contains(@class, "section-article")]') #extracts HTML from the start_url
        
    for article in articles:
        x = article.xpath('.//h3/a[2]') #extracts <a> tag from start _url 
        link = x.xpath('.//@href').extract_first()  #extracts URL for the articles recursively   
        print(link)
        #yield response.follow(link, callback = self.parse_news)   

def parse_news():
    headline = response.xpath('//h1[contains(@class, "article-heading margin")]/text()').extract_first() #scrapes headline 
    datetime = response.xpath('//span[contains(@class, "date")]/text()').extract_first() #scrapes datetime
    image = response.xpath('//div[contains(@class, "field-item")]/img/@src').extract_first() #scrapes image url 
    summary = response.xpath('//p[contains(@class, "margin")]/text()').extract_first() #scrapes summary of the news
    link = response.url
    
