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

### Upcoming
- Scheduling of Scraper using Scrapyd

*Tested on:*
```
Python==2.7.13
Scrapy==1.4.0
Psycopg2==2.7.3.2
```