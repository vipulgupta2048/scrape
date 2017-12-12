import requests
from flask import Flask, render_template, request
import json
from utils.db import DatabaseManager
import re
from utils.settings import logger

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

@application.route('/ajax/getitems')
def get_items():
    items= {
        'total': 0,
        'rows': []
    }
    sort = request.args.get("sort", default="id")
    order = request.args.get("order", default = "DESC")
    offset = request.args.get("offset", default = 1, type = int )
    limit = request.args.get("limit", default = 10, type = int)
    search = request.args.get("search", default="")

    if order != 'desc' or order != 'asc':
        order = 'DESC'
    order = order.upper()

    sort = re.sub(r'[^\w]', '' , sort)
    search = re.sub(r'[^\w]', '', search)
    search = "%"+search.lower()+"%"
    sql = "WITH res_main AS ( \
               SELECT s.site_name, l.* AS total FROM log_table \
               AS l JOIN site_table AS s ON l.site = s.id \
               WHERE LOWER(s.site_name) LIKE %s OR LOWER(l.shutdown_reason) LIKE %s OR l.id::text LIKE %s \
           ), res_count AS ( \
               SELECT COUNT(*) AS total FROM res_main \
           ) \
           SELECT * FROM res_main, res_count \
               ORDER BY res_main." + sort + " " + order + " \
               OFFSET %s FETCH NEXT %s ROWS ONLY;"
#    logger.error(sql)
    try:
        conn = DatabaseManager()
#        if len(search)>0:
#            search = "%"+search+"%"
#            sql += " WHERE s.site_name LIKE %s OR l.shutdown_reason LIKE %s OR l.id LIKE %s"
#            conn.cursor.execute(sql, (offset, limit, search, search, search))
#        else:
        conn.cursor.execute(sql, (search, search, search, offset, limit))

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


if __name__ == "__main__":
    application.run(host='0.0.0.0')
