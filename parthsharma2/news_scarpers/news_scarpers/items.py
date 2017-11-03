# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScarpersItem(scrapy.Item):
    title = scrapy.Field
    link = scrapy.Field
    date = scrapy.Field
    content = scrapy.Field
    image = scrapy.Field
    author = scrapy.Field
