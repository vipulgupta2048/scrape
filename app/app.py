import psycopg2
# from ...scrape.scrapeNews.envConfig import envConfig
USERNAME = 'scrapeuser'
PASSWORD = 'simple'
from flask import Flask, render_template
app = Flask(__name__)
# Setting up local variables USERNAME & PASSWORD
# PASSWORD = envConfig.PASSWORD
# USERNAME = envConfig.USERNAME

@app.route('/stats')
def stats():
    connection = psycopg2.connect(host='localhost',user='scrapeuser',database='scraped_news',password='simple')
    cursor = connection.cursor()
    cursor.execute("""SELECT site.id, site.site_name, COUNT(news.link), site.site_url FROM news_table AS news FULL OUTER JOIN site_table AS site ON news.site_id = site.id group by site.site_name, site.id, site.site_url having site.id <> 100 order by site.id ASC""")
    statData = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("stats.html",statistics = statData)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
