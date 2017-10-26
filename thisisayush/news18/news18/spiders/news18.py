import scrapy
import os
import json
import sys

class News18Spider(scrapy.Spider):
    name = "News18Spider"
    path = os.path.abspath(os.getcwd())
    urls_parsed = []
    start_url = "http://www.news18.com/news/"
    ignoreClasses = ["photoiconb", "photoicons", "vodeoiconb", "vodeoicons"]

    def __init__(self):
        self.load_urls_parsed()

    def start_requests(self):
        yield scrapy.Request(url = self.start_url, callback=self.parse)
    
    def parse(self, response):
        if response.status != 200:
            yield {"msg": "Status Code:"+response.status_code}
        else:
            news_sections = response.xpath('//div[contains(@class,"blog-list-blog")]')
            for section in news_sections:
                news_type = section.xpath("./a[1]/@class").extract_first()
                if news_type is not None:
                    flag = 0
                    news_type = news_type.split(" ")
                    for x in news_type:
                        if x in self.ignoreClasses:
                            flag = 1 
                            yield "\033[0;36;40m Skipping due to " + x + "\033[0m"   
                    if flag:
                        continue

                title = section.xpath("./p/a/text()").extract_first()
                print("\033[0;34;40m Title: "+ title + "\033[0m")
                href = response.urljoin(section.xpath("./p/a[1]/@href").extract_first())
                if href not in self.urls_parsed:
                    yield scrapy.Request(url = href, callback=self.parse_news)
                else:
                    print("\033[1;33;40m Already Parsed! Skipping... \033[0m")
                    yield {"msg":"Already Parsed"}

            next_page = response.xpath('//div[contains(@class, "pagination")]/ul/li[contains(@class,"next")]/a/@href').extract_first();
            if next_page not in self.urls_parsed and next_page is not None:
                yield scrapy.Request(url = response.urljoin(next_page))
        yield {"status": "Completed"}
        #print(response.xpath('//h1/text()').extract_first())
    
    def parse_news(self, response):
        news = {}
        news_url = response.url
        yield self.update_urls_parsed_file(news_url)
        news_title = response.xpath("//h1/text()").extract_first()
        news_excerpt = response.xpath("//h2[contains(@class, 'story-intro')]/text()").extract_first()
        news_picture = response.xpath("//div[contains(@class, 'articleimg')]/picture/source[1]/@srcset").extract_first()
        news = {'url': news_url, 'title': news_title, 'description': news_excerpt, 'image': news_picture};
        yield self.update_news_file(news)
    
    def update_news_file(self, news):
        try:
            existing_news = []
            try:
                news_file = open(self.path+'/data/news.json', "r")
                data = news_file.read()
                news_file.close()
                if len(data) >= 2:
                    existing_news = json.loads(data)
            except FileNotFoundError as e:
                print("\033[0;31;40m Creating File: news.json  \033[0m")
            existing_news.append(news)
            news_file = open(self.path+'/data/news.json', "w")
            news_file.write(json.dumps(existing_news))
            news_file.close()
            print("\033[0;32;0m Writing: "+news['title'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("\033[0;31;40m Error: ", exc_type, fname, exc_tb.tb_lineno, str(e), "\033[0m")
    
    def update_urls_parsed_file(self, url):
        try:
            self.load_urls_parsed()
            if url not in self.urls_parsed:
                self.urls_parsed.append(url)
                urls_parsed_file = open(self.path+'/data/urls_parsed.json', "w")
                urls_parsed_file.write(json.dumps(self.urls_parsed))
                urls_parsed_file.close()
        except Exception as e:
            print("\033[0;31;40m Error: " + str(e) + "\033[0m")

    def load_urls_parsed(self):
        try:
            urls_parsed_file = open(self.path+'/data/urls_parsed.json', "r")
            data = urls_parsed_file.read()
            if len(data) > 2:
                self.urls_parsed = json.loads(data)
                print("\033[1;34;40m URLS: "+ str(len(self.urls_parsed)) + "\033[0m")
            else:
                self.urls_parsed = []
            urls_parsed_file.close()
        except FileNotFoundError as e:
            print("\033[0;31;40m File Not Found: "+ str(e) + "\033[0m")
            urls_parsed_file = open(self.path+'/data/urls_parsed.json','w')
            urls_parsed_file.close()
            self.urls_parsed = []
        except Exception as e:
            print("\033[0;31;40m Error: " + str(e) + "\033[0m")

        



