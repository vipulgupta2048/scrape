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

- Requirements:
    - scrapy
    - requests
    - click
    - python-dateutil

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
    SPIDER_DETAILS = [
    # Add your Spiders in the following format.
    # {'site_id':'YOUR_SPIDER_ID','YOUR_SPIDER_NAME':'','site_url':'YOUR_SPIDER_URL'}
    {'site_id':100,'site_name':'EXAMPLE_SPIDER_NAME','site_url':'http://www.example.com'},
    {'site_id':101,'site_name':'Indian Express','site_url':'http://indianexpress.com/section/technology/'},
    {'site_id':102,'site_name':'India TV','site_url':'http://www.indiatvnews.com/business/tech/'},
    {'site_id':103,'site_name':'Time','site_url':'http://time.com/section/tech/'},
    {'site_id':104,'site_name':'NDTV','site_url':'https://www.ndtv.com/latest/page-1'},
    {'site_id':105,'site_name':'Inshorts','site_url':'http://www.inshorts.com/en/read/'}
	{'site_id':106,'site_name':'Zee News','site_url':'http://zeenews.india.com/india'}
    {'site_id':107,'site_name':'News18','site_url':'http://www.news18.com/news/'}
	{'site_id':108,'site_name':'moneyControl','site_url':'http://www.moneycontrol.com/news/business/'}
	]
    ```

    - Run setupDB.py
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
    6. zeeNews
    7. News18Spider
    8. moneyControl
    9. newsNation [In development]

- Options:
    1. To set the number of pages to be scraped use  `-a pages = X` (X = Number of pages).
	Applicable for:
        1. indianExpressTech
    	2. indiaTv  
    	3. timeTech

Happy collaborating !!   
