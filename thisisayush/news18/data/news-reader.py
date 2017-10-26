import json, os, time

while 1:
    file = open("news.json", "r")
    data = file.read()
    file.close()
    try: 
        news = json.loads(data)
    except Exception as e:
        print("JSON READ ERROR: "+str(e))
        continue
    print(" Total News Scanned: "+str(len(news)))
    time.sleep(3)



