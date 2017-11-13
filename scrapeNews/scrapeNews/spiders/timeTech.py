# -*- coding: utf-8 -*-
import json
import scrapy
from scrapeNews.items import ScrapenewsItem


class TimetechSpider(scrapy.Spider):
    name = 'timeTech'
    allowed_domains = ['time.com/wp-json/ti-api/v1/posts']

    def start_requests(self):
        params = '?time_section_slug=time-section-tech&_embed=wp:meta,wp:term,fortune:featured,fortune:primary_section,fortune:primary_tag,fortune:primary_topic&per_page=30'
        start_url = 'http://time.com/wp-json/ti-api/v1/posts/' + params
        yield scrapy.Request(url=start_url, callback=self.parse, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})

    def parse(self, response):
        newsBoxList = json.loads(response.text)
        item = ScrapenewsItem()  # Scraper Items
        for newsBox in newsBoxList:
            item['title'] = newsBox['title']['rendered'],
            item['link'] = newsBox['link'],
            item['newsDate'] = newsBox['modified'],
            # Relax, This line Takes the entire content (string), converts it
            # to a list of first 30 words and joins them with white space to
            # make it back to a string!
            item['content'] = ' '.join(str(newsBox['content']['plain']).split(' ')[:30]),
            item['image'] = newsBox['_embedded']['fortune:featured'][0]['image']['src']['square']
            item['source'] = 103
            yield item
