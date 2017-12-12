import logging
import os


DbDateFormat = "%Y-%m-%d %H:%M:%S %z"


# Logger Configuration (scrapeNews)
logger = logging.getLogger("scrapeNews")
handler = logging.FileHandler('scrapeNews.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s [Line %(lineno)d]  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

#DATABASE CONFIG

try:
    DB_INFO = {
        "host": os.environ['SCRAPER_DB_HOST'],
        "name": os.environ['SCRAPER_DB_NAME'],
        "user": os.environ['SCRAPER_DB_USER'],
        "password": os.environ['SCRAPER_DB_PASS']
    }
except KeyError as e:
    logger.critical("KeyError: "+str(e) + " not found")
    exit()
