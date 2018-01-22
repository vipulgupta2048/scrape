# On Your Mark, Get Set, Scrape !!

This repository holds the code for scrapers built under the project "Scrape the Planet"  
- Methods used for scraping : Scrapy   
- Language used for scraping : Python3.X.X

**Minutes of the meeting:** http://bit.ly/scrapeThePlanet

## Automatic Installation
Modify Hosts File ```scrapeNews/install/ansible/hosts``` and use ```ansible-playbook install.yaml -i hosts``` to automatically deploy the complete application on server.

## Manual Installation
Clone the repository (or download it). Then, follow the installation steps to run the spiders.

### Directory Structure
```
ROOT
|__ deploy
|_____ env.sh
|_____ web
|_______ web_app
|_______ scrapeNews
|_________ db.py
|_________ settings.py
|_____ logs
|_____ start
|_____ VENV_NAME
|__ scrape
```

### Create a Virtual Environemnt
path: ```ROOT/deploy/VENV_NAME```
```bash
python3 -m venv VENV_NAME
```
### Activate the venv
Windows: `VENV_NAME/Scripts/activate`
Linux: `source VENV_NAME/bin/activate`
### Install the requirements
Navigate to repository: `pip install -r requirements.txt`
- Requirements(For scraping):
    - scrapy
    - requests
    - python-dateutil
- Requirements (For database):
    - psycopg2
- Requirements (For flask Application):
    - flask
    - gunicorn
- Requirements (For deploying and scheduling spiders)
    - scrapyd
    - git+https://github.com/scrapy/scrapyd-client
    - schedule

### Install TOR and Privoxy
#### Install TOR
```bash
sudo apt-get install tor
```
#### Install Privoxy
```bash
sudo apt-get install privoxy
```
#### Configure Privoxy to route TOR
Add following lines at the end of ```/etc/privoxy/config```
```bash
forward-socks5  / 127.0.0.1:9050 .
forward-socks4a / 127.0.0.1:9050 .
forward-socks5t / 127.0.0.1:9050 .
```
#### Start TOR And Privoxy
```bash
sudo service tor start
sudo service privoxy start
```
### Database Setup (PostgreSQL)
#### Installation in Debian: 
```bash
sudo apt-get install postgresql postgresql-contrib
```
#### Make User:
**Note: Your USERNAME and PASSWORD must contain only smallcase characters.**
```bash
sudo -i -u postgres
createuser YOUR_ROLE_NAME/YOUR_USERNAME --interactive --pwprompt
```
### Make Environment Configuration File
path: ```ROOT/deploy/env.sh```
```bash
# Set The Environment Variables
export SCRAPER_DB_HOST="ENTER_VALUE_HERE"
export SCRAPER_DB_USER="ENTER_VALUE_HERE"
export SCRAPER_DB_PASS="ENTER_VALUE_HERE"
export SCRAPER_DB_NAME="ENTER_VALUE_HERE"
export SCRAPER_DB_TABLE_NEWS="ENTER_VALUE_HERE"
export SCRAPER_DB_TABLE_SITE="ENTER_VALUE_HERE"
export SCRAPER_DB_TABLE_LOG="ENTER_VALUE_HERE"
export FLASK_APP="ROOT/deploy/web/web_app/server.py"
```

### Install Web App

#### Copy Required Files
Copy ```ROOT/scrape/scrapeNews/web_app/*``` to ```ROOT/deploy/web/web_app/*```
Copy ```ROOT/scrape/scrapeNews/scrapeNews/settings.py``` to ```ROOT/deploy/web/scrapeNews/```
Copy ```ROOT/scrape/scrapeNews/scrapeNews/db.py``` to ```ROOT/deploy/web/scrapeNews/```

#### Install Nginx and Gunicorn
path: ```ROOT/deploy/```
```
sudo apt-get install nginx
source ROOT/deploy/VENV_NAME/bin/activate
pip install gunicorn
```
#### Install Nginx Config
Replace Vars in ```ROOT/scrape/scrapeNews/install/standard/nginx-site/scraper``` and copy it to ```/etc/nginx/sites-available/``` and create symbolic link:
```
sudo ln -s /etc/nginx/sites-available/scraper /etc/nginx/sites-enabled/scraper
sudo service nginx restart
```
### Install Systemd Service
Copy startup script from ```ROOT/scrape/scrapeNews/install/standard/start``` to ```ROOT/deploy/start```
Replace Vars in ```ROOT/scrape/scrapeNews/install/standard/systemd/scraper.service``` and copy it to ```/etc/systemd/system/```, enable the service:
```
sudo systemctl daemon-reload
sudo systemctl restart scraper
sudo systemctl enable scraper
```

## Run Spiders
**Note: Navigate to the folder containing scrapy.cfg**
path: ```ROOT\scrape\scrapeNews```
```bash
scrapy crawl SPIDER_NAME
```
### SPIDER_NAME List:
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
    17. newsNation
### Options (Depreciated)
To set the number of pages to be scraped use  `-a pages = X` (X = Number of pages to scrape).
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

To set the number of pages to be scraped use  `-a offset = X` (X = Number of pages to skip).
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

