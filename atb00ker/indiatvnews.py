import requests
from lxml import etree
from lxml import html
import json
with open ('data/indiatvnews.json','w+') as f:
    f.write('')
urls = []
newsData = []
pages = eval(input("Enter the number of pages you plan to scrap from IndiaTV: "))
for count in range(1 , pages+1):
    urls.append('http://www.indiatvnews.com/india/'+ str(count))
    for url in urls:
        data = requests.get(url).text
        et = html.fromstring(data)
        imagesContainer = et.xpath("//ul[@class='newsListfull']/li[@class='p_news']/a[@class='thumb']/img/@data-original")
        titlesContainer = et.xpath("//ul[@class='newsListfull']/li[@class='p_news']/div[@class='content']/h3[@class='title']/a/text()")
        linksContainer = et.xpath("//ul[@class='newsListfull']/li[@class='p_news']/div[@class='content']/h3[@class='title']/a/@href")
        timeContainer = et.xpath("//span[@class='deskTime']/text()")
        for image,title,link,time in zip(imagesContainer,titlesContainer,linksContainer,timeContainer):
            newsData.append({'image': image, 'title': title, 'link': link, 'time': time });
        with open ('data/indiatvnews.json','a') as f:
            f.write(json.dumps(newsData))
