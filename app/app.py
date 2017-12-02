import psycopg2
import sys
from flask import Flask, render_template
app = Flask(__name__)
# Setting up local variables USERNAME & PASSWORD
sys.path.append("./../scrapeNews/")
import envConfig
sys.path.append("./../app/")

# Setting up the project variables
PASSWORD = envConfig.PASSWORD
USERNAME = envConfig.USERNAME
NEWS_TABLE = envConfig.NEWS_TABLE
SITE_TABLE = envConfig.SITE_TABLE
LOG_TABLE = envConfig.LOG_TABLE
DATABASE_NAME = envConfig.DATABASE_NAME
HOST_NAME = envConfig.HOST_NAME

@app.route('/stats')
def stats():
    connection = psycopg2.connect(host=HOST_NAME,user=USERNAME,database=DATABASE_NAME,password=PASSWORD)
    cursor = connection.cursor()
    command = "SELECT site.id, site.site_name, COUNT(news.link), site.site_url FROM " + NEWS_TABLE + " AS news FULL OUTER JOIN " + SITE_TABLE + " AS site ON news.site_id = site.id group by site.site_name, site.id, site.site_url having site.id <> 100 order by site.id ASC"
    cursor.execute(command)
    statData = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("stats.html",statistics = statData)

@app.route('/ScrapeNewsErrorLog')
def ScrapeNewsErrorLog():
    with open("./../scrapeNews/scrapeNewsError.log","r") as logs:
        logsForHtml = []
        for lines in logs.readlines():
            logsForHtml.append("<pre>" + lines + "</pre>")
        return '\n'.join(logsForHtml)

if __name__ == "__main__":
    app.run()
