import json
import requests
import logging
from lxml import html


def scrape():
    try:
        response = html.fromstring(requests.get('https://www.inshorts.com/en/read').text)
    except requests.exceptions.RequestException as e:
        logging.error('Failed to establish a connection.')
        return;
    headlines = response.xpath('//a[@class="clickable"]/span/text()')
    authors = response.xpath('//span[@class="author"]/text()')
    time = response.xpath('//span[@class="time"]/text()')
    date = response.xpath('//span[@clas="date"]/text()')
    body = response.xpath('//div[@itemprop="articleBody"]/text()')
    try:
        with open('data.json', 'w') as f:
            for i in range(len(headlines)):
                json.dump({
                    'headline': headlines[i],
                    'author': authors[i],
                    'time': time[i],
                    'date': date[i],
                    'body': body[i],
                }, f)
    except IOError:
        logging.error('File could not be written.')



if __name__ == '__main__':
    scrape()
