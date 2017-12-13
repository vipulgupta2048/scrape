# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapenewsItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    newsDate = scrapy.Field()
    content = scrapy.Field()
    image = scrapy.Field()
#    source = scrapy.Field()


# item['title']
# item['link']
# item['newsDate']
# item['content']
# item['image']
# item['source']
