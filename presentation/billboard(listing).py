import logging
import requests
from lxml import html

def scrape():
    try:
        r = requests.get('http://www.billboard.com/charts/hot-100')
        logging.info(r)
    except requests.exceptions.RequestException as e:
        logging.error('Failed to establish a connection')
        return

    response = html.fromstring(r.text)
    cards = response.xpath('//article[contains(@class, "chart-row")]')
    song_titles = []
    artists = []
    for card in cards:
        song_titles.append(card.xpath('.//h2[@class="chart-row__song"]/text()')[0])
        if card.xpath('.//a[@class="chart-row__artist"]/text()'):
            artists.append(card.xpath('.//a[@class="chart-row__artist"]/text()')[0].strip())
        elif card.xpath('.//span[@class="chart-row__artist"]/text()'):
            artists.append(card.xpath('.//span[@class="chart-row__artist"]/text()')[0].strip())

    for i in range(len(song_titles)):
        print(i + 1, song_titles[i], "--", artists[i])


if __name__ == '__main__':
    scrape()
