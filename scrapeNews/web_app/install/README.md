### How to Install
- Install Gunicorn
- Install Nginx
- Replace paths accordingly in the files of this folder
- Copy Files to respective directories:
    - ```nginx-site/web_app``` -> ```/etc/nginx/sites-available/```
    - ```systemd/web_app.service``` -> ```/etc/systemd/system/```
- Register Nginx Site as: ```sudo ln -s /etc/nginx/sites-enabled/web_app /etc/nginx/sites-available/web_app
- Start Gunicorn Service: ```sudo systemctl start web_app```
- Register Gunicorn Service to Auto Start: ```sudo systemctl enable web_app```
- If everything goes fine, you shouldn't see any errors in ```scrapeNews.log```

Server is now accessible at port 5009
