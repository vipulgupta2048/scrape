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

### Database Setup (Postgresql)

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
	- `sudo -i -u postgres`
	- `createuser scrapeuser --interactive --pwprompt`
	- Enter name of role to add: `scrapeuser`

- Setup Database:
	- Insert your password.
	- Insert your spider details.
	- Run: `python3 setupDB.py`

## Run Spiders
**Note: Navigate to the folder containing scrapy.cfg**
```
scrapy crawl SPIDER_NAME -o DATA_FILE.json
```

- SPIDER_NAME List:
	1. indianExpressTech
	2. indiaTv
	3. timeTech

Happy collaborating !!   
