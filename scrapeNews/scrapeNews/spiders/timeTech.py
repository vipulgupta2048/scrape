# -*- coding: utf-8 -*-
import scrapy
#from scrapeNews.pipelines import InnerSpiderPipeline as pipeline
from scrapeNews.items import ScrapenewsItem
from scrapeNews.settings import logger
from scrapeNews.db import DatabaseManager, LogsManager

class TimetechSpider(scrapy.Spider):

    custom_settings = {
        'site_name': "Time",
        'site_url': "http://time.com/section/tech/",
        'site_id': -1,
        'log_id': -1,
        'url_stats': {'parsed': 0, 'scraped': 0, 'dropped': 0, 'stored': 0}
    }

    start_url = "http://time.com/section/tech/?page=1"

    def parse(self, response):
        if response.status != 200:
            logger.error(__name__ + " Non-200 Response Received " + response.status + " for url" + response.url)
            return False
        try:

            next_page = response.xpath("//a[@rel='next']/@href").extract_first()
            if next_page != None:
                # For the large newsBox in top of all the pages. (In Normal Pages) or sends all request for all the articles in API page or sends the request for the special page.
                try:
                    newsBox = 'http://www.time.com' + response.xpath("//div[@class='partial hero']/article/a/@href").extract_first()
                    if not DatabaseManager().urlExists(link):
                        self.custom_settings['url_stats']['parsed'] += 1
                        yield scrapy.Request(url=newsBox, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
                except Exception as Error:
                    if newsBox.xpath("//main[contains(@class,'content article')]"):
                        self.custom_settings['url_stats']['parsed'] += 1
                        yield scrapy.Request(url=newsBox, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
                    elif newsBox.xpath("//div[contains(@class,'_29M-6C9w')]"):
                        newsContainer = newsBox.xpath("//div[contains(@class,'_29M-6C9w')]//div[contains(@class,'_2cCPyP5f')]//a[@class='_2S9ChopF']/@href")
                        for link in newsContainer:
                            if not DatabaseManager().urlExists(link):
                                self.custom_settings['url_stats']['parsed'] += 1
                                yield scrapy.Request(url=link, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
                    else:
                        logger.error(__name__ + " Error in Parsing : " + response.url)

                # For the rest of the boxes
                newsContainer = response.xpath("//div[@class='partial marquee']/article")
                for newsBox in newsContainer:
                    link = 'http://www.time.com' + newsBox.xpath('a/@href').extract_first()
                    if not DatabaseManager().urlExists(link):
                        self.custom_settings['url_stats']['parsed'] += 1
                        yield scrapy.Request(url=link, callback=self.parse_article, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
                    else:
                        self.custom_settings['url_stats']['dropped'] += 1

                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page,self.parse)

        except Exception as e:
             logger.error(__name__ + " Unhandled: " + str(e))


    def parse_article(self, response):
        item = ScrapenewsItem()  # Scraper Items
        item['image'] = self.getPageImage(response)
        item['title'] = self.getPageTitle(response)
        item['content'] = self.getPageContent(response)
        item['newsDate'] = self.getPageDate(response)
        item['link'] = response.url
        item['source'] = 103
        if item['image'] is not 'Error' or item['title'] is not 'Error' or item['content'] is not 'Error' or item['newsDate'] is not 'Error':
            self.custom_settings['url_stats']['scraped'] += 1
            yield item
        else:
            self.custom_settings['url_stats']['dropped'] += 1
            yield None


    def getPageTitle(self, response):
        data = response.xpath('//h1[@itemprop="headline"]/text()').extract_first()
        if (data is None):
            data = response.xpath("//h1[contains(@class,'headline')]/text()").extract_first()
        if (data is None):
            data = response.xpath("//h1[@class='_8UFs4BVE']/text()").extract_first()
        if (data is None):
            data = response.xpath("//span[@class='xxx_oneoff_special_story_v3_headline']/text()").extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to Extract Title : " +response.url)
            data = 'Error'
        return data


    def getPageImage(self, response):
        data = response.xpath("//meta[@property='og:image']/@content").extract_first()
        if (data is None):
            logger.error(__name__ + " Unable to extract Image : " + response.url)
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
                logger.error(__name__ + " Unable to Extract Date: " + response.url)
                data = 'Error'
        except Exception as Error:
            logger.error(__name__ + " Unable to Extract Date: " + response.url + " : " + str(Error))
            data = 'Error'
        finally:
            return data


    def getPageContent(self, response):
        try:
            data =  ' '.join((''.join(response.xpath("//div[@id='article-body']/div/p/text()").extract())).split(' ')[:40])
            if not data:
                data =  ' '.join((''.join(response.xpath("//section[@class='chapter']//text()").extract())).split(' ')[:40])
                if not data:
                    data =  ' '.join(''.join(response.xpath("//div[contains(@class,'-5s7sjXv')]/div/div/article/p/text()").extract()).split()[:40])
                    if not data:
                        data =  response.xpath("//div[contains(@class,'_1Joi0PLr')]//span/text()").extract_first()
                        if not data:
                            logger.error(__name__ + " Unable to Extract Content : " + response.url)
                            data = 'Error'
        except Exception as Error:
            logger.error(__name__ + " Unable to Extract Content : " + response.url + " :: " + str(Error))
            data = 'Error'
        return data

    def closed(self, reason):
        if not LogsManager().end_log(self.custom_settings['log_id'], self.custom_settings['url_stats'], reason):
            logger.error(__name__ + " Unable to end log for spider " + self.name + " with url stats: " + str(self.custom_settings['url_stats']))