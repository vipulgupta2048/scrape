import requests
from lxml import etree, html

def scrapeCommunityGov():
    urls = ['https://community.data.gov.in/all-blogs/page/5/','https://community.data.gov.in/all-blogs/page/4/','https://community.data.gov.in/all-blogs/page/3/','https://community.data.gov.in/all-blogs/page/2/','https://community.data.gov.in/all-blogs/page/1/']
    govData = []
    for url in urls:
        parentData = requests.get(url).text
        parentResponse = html.fromstring(parentData)
        pageLinks = parentResponse.xpath("//figcaption/p/a/@href")

        for link in pageLinks:
            childData = requests.get(link).text
            childResponse = html.fromstring(childData)
            # ''.join() used to convert the list response to a single string.
            imageContainer = ''.join(childResponse.xpath("//div[@class='grid-holder-inner clearfix']/p/img/@src"))
            titleContainer = ''.join(childResponse.xpath("//div[@class='grid-holder-inner clearfix']/h2/text()"))
            timeContainer = ''.join(childResponse.xpath("//div[@class='grid-holder-inner clearfix']/span[1]/text()"))
            contentContainer = ''.join(childResponse.xpath("//div[@class='grid-holder-inner clearfix']/p/text()"))
            govData.append({'image': imageContainer , 'title': titleContainer, 'content': contentContainer, 'time': timeContainer})
        print (govData)
if __name__ == '__main__':
    scrapeCommunityGov()
