import json
import requests
from lxml import html

def scrape():
    response = html.fromstring(requests.get('https://www.inshorts.com/en/read').text)
    headlines = response.xpath('//a[@class="clickable"]/span/text()')
    authors = response.xpath('//span[@class="author"]/text()')
    time = response.xpath('//span[@class="time"]/text()')
    date = response.xpath('//span[@clas="date"]/text()')
    body = response.xpath('//div[@itemprop="articleBody"]/text()')
    with open('data.json', 'w') as f:
        for i in range(len(headlines)):
            json.dump({
                'headline': headlines[i],
                'author': authors[i],
                'time': time[i],
                'date': date[i],
                'body': body[i],
            }, f)


if __name__ == '__main__':
    scrape()
