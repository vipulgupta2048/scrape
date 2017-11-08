import requests
from lxml import etree, html
import click

@click.command()
@click.option('--pages', default=1, help='Number of pages')

def scrapeNews(pages):
    urls = []
    newsData = []
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
            newsData.append({'image': image, 'title': title, 'link': link, 'time': time })
        print (newsData)

if __name__ == '__main__':
    scrapeNews()
