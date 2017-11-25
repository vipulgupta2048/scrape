# -*- coding: utf-8 -*-
import scrapy
from scrapeNews.items import ScrapenewsItem
import logging
loggerError = logging.getLogger("scrapeNewsError")

class TimetechSpider(scrapy.Spider):
    name = 'timeTech'

    def __init__(self, pages=4, *args, **kwargs):
        super(TimetechSpider, self).__init__(*args, **kwargs)
        for count in range(1 , int(pages)+1):
            self.start_urls.append('http://time.com/section/world/?page='+ str(count))


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)
            yield scrapy.Request(url=url, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})


    def parse(self, response):
        # For the large newsBox in top of all the pages.
        newsBox = 'http://www.time.com' + response.xpath("//div[@class='partial hero']/article/a/@href").extract_first()
        yield scrapy.Request(url=newsBox, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
        # For the rest of the boxes
        newsContainer = response.xpath("//div[@class='partial marquee']/article")
        for newsBox in newsContainer:
            link = 'http://www.time.com' + newsBox.xpath('a/@href').extract_first()
            yield scrapy.Request(url=link, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = self.getPageLink(response)
        item['source'] = 103
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['link'] is not 'Error' or item['newsDate'] is not 'Error':
            yield item


    def getPageTitle(self, response):
        data = response.xpath("//h1[contains(@class,'headline')]/text()").extract_first()
        if (data is None):
            data = response.xpath("//h1[@class='_8UFs4BVE']/text()").extract_first()
        if (data is None):
            data = response.xpath("//span[@class='xxx_oneoff_special_story_v3_headline']/text()").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageLink(self, response):
        data = response.url
        if (data is None):
            loggerError.error(response)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath("//meta[@property='og:image']/@content").extract_first()
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


    def getPageDate(self, response):
        try:
            # split used to Spit Data in Correct format!
            data = (str(response.xpath("//script[@type='application/ld+json']").extract_first()).split('datePublished":"',1)[1])[:19]
        except (TypeError,IndexError) as Error:
            # This fail case works only on very specific articles.
            scriptData = None
            scriptsList = response.xpath("/html/head/script[not(contains(@type,'text/javascript'))]")
            for script in scriptsList:
                try:
                    scriptData = (script.extract()).split("<script>utag_data",1)[1]
                    break
                except:
                    continue
            if (scriptData is not None):
                data = (scriptData.split('"publish_date":"',1)[1]).split("+",1)[0]
            if (data is None):
                loggerError.error(response.url)
                data = 'Error'
        finally:
            return data


    def getPageContent(self, response):
        data =  ' '.join((''.join(response.xpath("//div[@id='article-body']/div/p/text()").extract())).split(' ')[:40])
        if (data is None):
            loggerError.error(response.url)
            data = 'Error'
        return data


# DEAD API's Link: 'time.com/wp-json/ti-api/v1/posts?time_section_slug=time-section-tech&_embed=wp:meta,wp:term,fortune:featured,fortune:primary_section,fortune:primary_tag,fortune:primary_topic&per_page=30&page1'
