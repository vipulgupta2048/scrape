import scrapy 
from scrapy.crawler import CrawlerProcess
from spiders.hindustan import HindustanSpider
from spiders.ndtv_scraper import NdtvScraperSpider
from scrapy.utils.project import get_project_settings


#obj = HindustanSpider()
obj2 = NdtvScraperSpider()
process = CrawlerProcess(get_project_settings())

process.crawl(obj2)
process.start()