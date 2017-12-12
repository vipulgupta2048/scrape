# On Your Mark, Get Set, Scrape !!

This repository holds the code for scrapers built under the project "Scrape the Planet"  
- Methods used for scraping : Scrapy   
- Language used for scraping : Python3.X.X

**Minutes of the meeting:** http://bit.ly/scrapeThePlanet

## Installation
Clone the repository (or download it). Then, follow the installation steps to run the spiders.

### Create a Virtual Environemnt
```
python3 -m venv VENV_NAME
```

### Activate the venv
Windows: `VENV_NAME/Scripts/activate`

Linux: `source VENV_NAME/bin/activate`

### Install the requirements
Navigate to repository: `pip3 install -r requirements.txt`

- Requirements(For scraping):
    - scrapy
    - requests
    - python-dateutil

- Requirements(For database):
    - psycopg2

- Requirements(For flask Application):
    - flask

### Database Setup (PostgreSQL)

**Note: You can comment out the following code in settings.py to avoid using pipelines.**

```
ITEM_PIPELINES = {
   'scrapeNews.pipelines.ScrapenewsPipeline': 300
}
```

- Installation in Debian: `sudo apt-get install postgresql postgresql-contrib`

- Configurations:
	- config: `/etc/postgresql/9.5/main`  
	- data:   `/var/lib/postgresql/9.5/main`
	- socket: `/var/run/postgresql`
	- port:   `5432`

- Make User:
	**Note: Your USERNAME and PASSWORD must contain only smallcase characters.**
	- `sudo -i -u postgres`
	- `createuser YOUR_ROLE_NAME/YOUR_USERNAME --interactive --pwprompt`

- Setup Database:
    - Create file a scrapeNews/envConfig.py; Inside it, Write:
    ```
    USERNAME = 'YOUR_ROLE_NAME/YOUR_USERNAME'
    PASSWORD = 'YOUR_PASSWORD'
    NEWS_TABLE = 'NEWS_TABLE_NAME'
    SITE_TABLE = 'SITE_TABLE_NAME'
    LOG_TABLE = 'LOG_TABLE_NAME'
    DATABASE_NAME = 'DATABASE_NAME'
    HOST_NAME = 'HOST_NAME'
    ```

## Run Spiders
**Note: Navigate to the folder containing scrapy.cfg**
```
scrapy crawl SPIDER_NAME
```
- SPIDER_NAME List:
	1. indianExpressTech
	2. indiaTv  
	3. timeTech
	4. ndtv
	5. inshorts
    6. zee
    7. News18Spider
    8. moneyControl
    9. oneindia
    10. oneindiaHindi
    11. firstpostHindi
    12. firstpostSports
    13. newsx
    14. hindustan
    15. asianage
    16. timeNews
    17. newsNation [In development]

- Options:
    1. To set the number of pages to be scraped use  `-a pages = X` (X = Number of pages to scrape).
	Applicable for:
        1. indianExpressTech
    	2. indiaTv  
    	3. timeTech
        4. moneyControl
        5. oneindia
        6. oneindiaHindi
        7. firstpostHindi
        8. firstpostSports
        9. newsx
        10. asianage
		11. ndtv
        12. timeNews

    2. To set the number of pages to be scraped use  `-a offset = X` (X = Number of pages to skip).
	Applicable for:
        1. indianExpressTech
    	2. indiaTv  
    	3. timeTech
        4. moneyControl
        5. oneindia
        6. oneindiaHindi
        7. firstpostHindi
        8. firstpostSports
        9. newsx
        10. asianage
        11. timeNews

Happy collaborating !!   
