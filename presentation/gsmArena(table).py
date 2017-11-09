import requests
from lxml import etree, html
import click

@click.command()
@click.option('--phone', default='OnePlus 5T', help='Phone you want to search')

def scrapeGsm(phone):
    phoneData = []
    gsmArenaData = []
    parentUrl = 'https://www.gsmarena.com/res.php3?sSearch=' + phone
    parentData = requests.get(parentUrl).text
    parentResponse = html.fromstring(parentData)
    links = parentResponse.xpath("//div[@class='makers']/ul/li/a/@href")
    for link in links:
        childData = requests.get('https://www.gsmarena.com/'+link).text
        childResponse = html.fromstring(childData)
        tableContainer = childResponse.xpath("//div[@id='specs-list']/table")
        for tableItem in tableContainer:
            tHead = tableItem.xpath(".//th/text()")
            tSectionHead = tableItem.xpath(".//tr/td[@class='ttl']/a/text()")
            tSectionBody = tableItem.xpath(".//tr/td[@class='nfo']//text()")
            phoneData.append({'tHead': tHead, 'tSectionHead': tSectionHead, 'tSectionBody': tSectionBody})
        gsmArenaData.append(phoneData)
    print (gsmArenaData[0])

if __name__ == '__main__':
    scrapeGsm()
