# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # ame = scrapy.Field()
     name = scrapy.Field()
     genus = scrapy.Field()
     species = scrapy.Field()
     pass
