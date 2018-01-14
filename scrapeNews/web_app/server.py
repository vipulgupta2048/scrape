import requests
from flask import Flask, render_template, request
import json
from scrapeNews.db import postgresSQL
import re
from scrapeNews.settings import logger, DB_INFO

application = Flask(__name__)

@application.route('/')
def home():
    return render_template('index.html')

@application.route('/browse')
def browse():
    return render_template('browse.html')

@application.route('/logs')
def logsView():
    return render_template('logs.html')

@application.route('/jobs')
def jobsView():
    return render_template('jobs.html')

@application.route('/stats')
def statsView():
    connection = postgresSQL()
    command = "SELECT site.id, site.site_name, COUNT(news.link) AS links, \
               site.site_url, logs.close_reason AS status FROM " \
               + DB_INFO['NEWS_TABLE'] + " AS news FULL OUTER JOIN " \
               + DB_INFO['SITE_TABLE'] + " AS site ON news.site_id = site.id FULL OUTER JOIN \
               (SELECT innerGroup.spider_id AS spider_id, COUNT(innerGroup.close_reason) AS close_reason \
               FROM (SELECT innerLogs.spider_id, innerLogs.close_reason FROM " \
               + DB_INFO['SITE_TABLE'] + " AS innerSite RIGHT JOIN \
               (SELECT spider_id, close_reason, start_time FROM " \
               + DB_INFO['LOG_TABLE'] + " WHERE (close_reason <> 'finished' \
               AND close_reason = 'crawling' AND ((start_time + '00:30:00') < NOW())) \
               OR (urls_parsed <> (urls_dropped + urls_scraped)) \
               OR (urls_stored <> urls_scraped) \
               OR (close_reason <> 'finished' AND close_reason <> 'crawling')) \
               AS innerLogs ON innerSite.id = innerLogs.spider_id \
               WHERE innerLogs.start_time > innerSite.status_check) AS innerGroup \
               GROUP BY innerGroup.spider_id) AS logs ON site.id=logs.spider_id \
               GROUP BY logs.close_reason, site.id ORDER BY site.id"
    connection.cursor.execute(command)
    statData = connection.cursor.fetchall()
    return render_template("stats.html", statistics = statData)

@application.route("/resetRequest", methods=["POST"])
def resetSpider():
    data = str(request.stream.read().decode('utf-8'))
    connection = postgresSQL()
    command = "UPDATE " + connection.site_table_name + " SET status_check=NOW() WHERE id= %s;"
    connection.cursor.execute(command, (data,))
    return str({"status": "ok"})

@application.route('/ajax/get/<resource>')
def get_items(resource):

    sort = request.args.get("sort", default="id")
    order = request.args.get("order", default = "DESC")
    offset = request.args.get("offset", default = 1, type = int )
    limit = request.args.get("limit", default = 10, type = int)
    search = request.args.get("search", default="")

    if order != 'desc' and order != 'asc':
        order = 'DESC'
    order = order.upper()

    sort = re.sub(r'[^\w]', '' , sort)
    search = re.sub(r'[^\w]', '', search)
    search = "%"+search.lower()+"%"

    if resource == "logs":
       sql = "WITH res_main AS ( \
                   SELECT s.site_name, s.spider_name, l.* FROM log_table \
                   AS l JOIN site_table AS s ON l.site = s.id \
                   WHERE LOWER(s.site_name) LIKE %s OR LOWER(l.shutdown_reason) LIKE %s OR l.id::text LIKE %s \
               ), res_count AS ( \
                   SELECT COUNT(*) AS total FROM res_main \
               )";
       queries = (search, search, search, offset, limit)

       return get_logs_or_items(sql, sort, order, queries)

    elif resource == "items":
       sql = "WITH res_main AS ( \
                  SELECT s.site_name, s.spider_name, i.* FROM item_table \
                  AS i JOIN site_table AS s ON i.site_id = s.id \
                  WHERE LOWER(s.site_name) LIKE %s OR LOWER(i.title) LIKE %s OR LOWER(i.link) LIKE %s OR LOWER(i.content) LIKE %s \
                  OR i.id::text LIKE %s \
              ), res_count AS ( \
                   SELECT COUNT(*) AS total FROM res_main \
              )"
       queries = (search, search, search, search, search, offset, limit)

       return get_logs_or_items(sql, sort, order, queries)

    elif resource == "jobs":
        return get_jobs()

    else:
        return json.dumps({"status": "Invalid Resource!"})

def get_logs_or_items(sql, sort, order, queries):

    items = {
        'total': 0,
        'rows': []
    }

    filter_str = "SELECT * FROM res_main, res_count \
                   ORDER BY res_main." + sort + " " + order + " \
                   OFFSET %s FETCH NEXT %s ROWS ONLY;"

    sql += filter_str

    try:
        conn = postgresSQL()
        conn.cursor.execute(sql, queries)

        data = conn.cursor.fetchall()
        for row in data:
            item = {}
            for column in row:
                if column == "total":
                    pass
                item[column] = str(row[column])
            items['rows'].append(item)
        if data != None:
            items['total'] = data[0]['total']
        else:
            items['total'] = 0
    except Exception as e:
        items['total'] = 0
        logger.error(__name__ + " " +str(e))
    return json.dumps(items)

def get_jobs():

    api_url = "http://localhost:6800/listjobs.json?project=scrapeNews"

    items = {
        'total': 3,
        'pending': {
            'total': 0,
            'rows' : []
        },
        'completed': {
            'total': 0,
            'rows' : []
        },
        'running': {
            'total': 0,
            'rows' : []
        }
    }

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            jobs = response.json()

            for job in jobs['pending']:
                x = {}
                x['job_id'] = job['id']
                x['spider_name'] = job['spider']
                items['pending']['rows'].append(x)
                items['pending']['total'] += 1

            for job in jobs['running']:
                x = {}
                x['job_id'] = job['id']
                x['spider_name'] = job['spider']
                x['start_time'] = job['start_time']
                items['running']['rows'].append(x)
                items['running']['total'] += 1

            for job in jobs['finished']:
                x = {}
                x['job_id'] = job['id']
                x['spider_name'] = job['spider']
                x['start_time'] = job['start_time']
                x['end_time'] = job['end_time']
                items['completed']['rows'].append(x)
                items['completed']['total'] += 1

        return json.dumps(items)
    except Exception as e:
        logger.error(__name__ + " Unhandled: " + str(e))

if __name__ == "__main__":
    application.run(host='0.0.0.0')
