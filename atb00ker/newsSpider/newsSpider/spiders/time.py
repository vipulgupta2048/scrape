# -*- coding: utf-8 -*-
# This is an Incomplete code and i am leaving it at this state, it will generate incorrect data every now and then!
# It takes forever to run and isn't even async, a shame even after using the awesome scrapy!

import scrapy
import requests
import os.path
import time
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from lxml import html
from lxml import etree
import json
import logging

class TimeSpider(scrapy.Spider):
    name = 'time'
    start_urls = ''

    def __init__(self):
        pages = eval(input("Enter the number of pages you want to scrape: "))
        self.driver = webdriver.Firefox(executable_path= str(os.getcwd()) + '/geckodriver')
        LOGGER.setLevel(logging.WARNING)
        self.driver.set_page_load_timeout(100)
        self.driver.get('http://time.com/section/tech/')
        for counter in range(1,pages):
            next = self.driver.find_element_by_xpath('//button[@class="mdl_R80l"]')
            next.click()
            time.sleep(5)
        response = self.driver.page_source
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
                linkData = requests.get(link, headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}).text
                et = html.fromstring(linkData)
                pageTimeList = et.xpath('//div[contains(@class,"color-darker-gray")]/text()')
                pageImageList = et.xpath('//picture/img/@src')
                if pageImageList and pageTimeList:
                    pageTime = pageTimeList[0]
                    pageImage = pageImageList[0]
                else:
                    self.driver.get(link)
                    infoPage = html.fromstring(self.driver.page_source)
                    if not pageTimeList and not pageImageList:
                        pageTime = self.getPageTime(infoPage)
                        pageImage = self.getPageImage(infoPage)
                    elif not pageImageList:
                        pageTime = pageTimeList[0]
                        pageImage = self.getPageImage(infoPage)
                    elif not pageTimeList:
                        pageTime = self.getPageTime(infoPage)
                        pageImage = pageImageList[0]
                    else:
                        print ('Unexpected Error occured for values: \nTime: ', pageTimeList, "\nImage: ", pageImageList)
                timeContainer.append(pageTime)
                imagesContainer.append(pageImage)
            except:
                print ("Error 101: Problem while fetching article data.")
                timeContainer.append('Error!')
                imagesContainer.append('Error!')
        self.driver.close()
        for image,title,link,date in zip(imagesContainer,titlesContainer,linksContainer,timeContainer):
            newsData.append({'image': image, 'title': title, 'link': link, 'time': date })
        with open ('time.json','w+') as f:
            f.write(json.dumps(newsData))
            os.rename('time.json','../data/time.json')


    def getPageTime(self, timePage):
        try:
            pageTime = timePage.xpath('//div[contains(@class,"timestamp")]/text()')
        except:
            print ("Error 103: Problem while storing time.", pageTime)
            pageTime = 'Error!'
        finally:
            return pageTime


    def getPageImage(self, videoPage):
        try:
            pageImageStyle = videoPage.xpath("//div[@class='vjs-poster']/@style")
            pageImageContainer = str(pageImageStyle).split('"')
            pageImage = pageImageContainer[1]
        except:
            try:
                pageImageContainer = videoPage.xpath("//div[contains(@class,'_5ihbkgAj')]/img/@src")
                pageImage = pageImageContainer[0]
            except:
                print ("Error 102: Problem while storing image.", pageImageContainer)
                pageImage = 'Error!'
        finally:
            return pageImage
