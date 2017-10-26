# -*- coding: utf-8 -*-
import scrapy
import requests
import os.path
import time
from selenium import webdriver
from lxml import html
from lxml import etree
import json
class TimeSpider(scrapy.Spider):
    name = 'time'
    start_urls = ''
    def __init__(self):
        pages = eval(input("Enter the number of pages you want to scrape: "))
        self.driver = webdriver.Firefox(executable_path= str(os.getcwd()) + '/geckodriver')
        self.driver.get('http://time.com/section/tech/')
        for counter in range(1,pages):
            next = self.driver.find_element_by_xpath('//button[@class="mdl_R80l"]')
            next.click()
            time.sleep(5)
        response = self.driver.page_source
        self.driver.close()
        # Used for bug fixing!
        # with open ('savedCopy.html','w+') as f:
        #     f.write(response)
        # with open ('savedCopy.html','r') as f:
        #     response = f.read()
        return self.parseNews(response)

    def parseNews(self, response):
        linksContainer = []
        timeContainer = []
        imagesContainer = []
        newsData = []
        response = html.fromstring(response)
        titlesContainer = response.xpath('//div[contains(@class,"_3vaerisi")]//a[contains(@class,"_2U6Dq8dR")]/text()')
        linksCollection = response.xpath('//div[contains(@class,"_3vaerisi")]//a[@class="_2S9ChopF"]/@href')
        for link in linksCollection:
            link = 'http://time.com' + str(link)
            linksContainer.append(link)
            try:
                linkData = requests.get(link, headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'})
                linkData = linkData.text
                et = html.fromstring(linkData)
                pageTime = et.xpath('//div[@class="row text font-accent size-1x-small color-darker-gray"]/text()')
                pageImage = et.xpath('//picture/img/@src')
                # if not pageImage:
                #     pageGImage = et.xpath("//*[@id='vjs_video_3']/div[2]")
                #     # pageImage = pageImage.split('"')
                #     print (pageGImage)
                timeContainer.append(pageTime)
                imagesContainer.append(pageImage)
                # print (pageTime)
            except:
                print ("Error 101: Problem while fetching article date.")
                timeContainer.append('Error in Loading')
                imagesContainer.append('Error in Loading')
        for image,title,link,date in zip(imagesContainer,titlesContainer,linksContainer,timeContainer):
            newsData.append({'image': image, 'title': title, 'link': link, 'time': date })
        with open ('time.json','w+') as f:
            f.write(json.dumps(newsData))
            os.rename('time.json','../data/time.json')
