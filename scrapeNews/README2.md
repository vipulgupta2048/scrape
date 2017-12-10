# News18 Scraper (thisisayush)

Author: Ayush Agarwal (@thisisayush)

This folder contains scraping code for News18.com
Start_Url: http://www.news18.com/news/

- Parses Continously until end of next_page is reached.
- Requires PostgreSQL for storing scraped data.
- Duplicates Filtering
- Logging

### Set Environment Variables
This script requires following Environment Variables to be set:
```
SCRAPER_DB_HOST
SCRAPER_DB_NAME
SCRAPER_DB_USER
SCRAPER_DB_PASS
```
### Install TOR and Privoxy 

#### Install TOR
```
sudo apt-get install tor
```
#### Install Privoxy
```
sudo apt-get install privoxy
```
#### Configure Privoxy to route TOR
Add following lines at the end of  ```/etc/privoxy/config```
```
forward-socks5  / 127.0.0.1:9050 .
forward-socks4a / 127.0.0.1:9050 .
forward-socks5t / 127.0.0.1:9050 .
```

### Upcoming
- Scheduling of Scraper using Scrapyd

*Tested on:*
```
Python==2.7.13
Scrapy==1.4.0
Psycopg2==2.7.3.2
```
