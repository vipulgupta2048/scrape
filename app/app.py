import psycopg2
import sys
from flask import Flask, render_template, request
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
    connection.autocommit = True
    command = "SELECT site.id, site.site_name, COUNT(news.link) AS links, site.site_url, logs.close_reason AS status FROM " + NEWS_TABLE + " AS news FULL OUTER JOIN " + SITE_TABLE +" AS site ON news.site_id = site.id FULL OUTER JOIN (SELECT innerGroup.spider_id AS spider_id, COUNT(innerGroup.close_reason) AS close_reason FROM (SELECT innerLogs.spider_id, innerLogs.close_reason FROM " + SITE_TABLE + " as innerSite RIGHT JOIN (SELECT spider_id, close_reason, start_time FROM " + LOG_TABLE + " WHERE (close_reason <> 'finished' AND close_reason = 'crawling' AND ((start_time + '00:30:00') < NOW())) OR (urls_parsed <> (urls_dropped + urls_scraped)) OR (urls_stored <> urls_scraped) OR (close_reason <> 'finished' AND close_reason <> 'crawling')) AS innerLogs ON innerSite.id = innerLogs.spider_id WHERE innerLogs.start_time > innerSite.status_check) AS innerGroup GROUP BY innerGroup.spider_id) AS logs ON site.id=logs.spider_id GROUP BY logs.close_reason, site.id ORDER BY site.id"
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

@app.route("/resetRequest", methods=["POST"])
def resetSpider():
    data = str(request.stream.read().decode('utf-8'))
    connection = psycopg2.connect(host=HOST_NAME,user=USERNAME,database=DATABASE_NAME,password=PASSWORD)
    cursor = connection.cursor()
    connection.autocommit = True
    command = "UPDATE " + SITE_TABLE + " SET status_check=NOW() WHERE id=" + str(data) + ";"
    cursor.execute(command)
    cursor.close()
    connection.close()
    return "Done"


if __name__ == "__main__":
    app.run()
