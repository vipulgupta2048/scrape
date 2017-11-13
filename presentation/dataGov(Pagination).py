import requests
from lxml import etree, html
import click

@click.command()
@click.option('--pages', default=1, help='Number of pages')

def scrapeGov(pages):
    urls = []
    govData = []
    for count in range(1 , pages+1):
        urls.append('https://data.gov.in/catalogs#sort_by=created&sort_order=DESC&items_per_page=9&page='+ str(count-1))
    for url in urls:
        data = requests.get(url).text
        response = html.fromstring(data)

        titlesContainer = response.xpath("//div[contains(@class,'view view-catalogs')]//div[@class='view-content']/div[contains(@class,'views-row')]/div[@class='views-field views-field-title']/span/a/text()")

        fieldContainer = response.xpath("//div[contains(@class,'view view-catalogs')]//div[contains(@class,'views-row')]/div[contains(@class,'department')]/span[@class='field-content']/text()")

        linksContainer = response.xpath("//div[contains(@class,'view view-catalogs')]//div[@class='view-content']/div[contains(@class,'views-row')]/div[@class='views-field views-field-title']/span/a/@href")

        for field,title,link in zip(fieldContainer,titlesContainer,linksContainer):
            govData.append({'field': field, 'title': title, 'link': "https://data.gov.in" + link})
        print (govData)

if __name__ == '__main__':
    scrapeGov()
