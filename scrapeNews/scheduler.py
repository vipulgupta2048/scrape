import requests
import schedule
import time
from datetime import datetime
from time import strftime
import logging

api_url = "http://localhost:6800/"

logger = logging.getLogger("news18Scheduler")
handler = logging.FileHandler('news18Scheduler.log')
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def scheduleScheduler():
    schedule.every().day.at("20:10").do(scheduleAllSpiders).tag("daily-task")

def scheduleRechecking():
    schedule.clear("daily-task")
    schedule.every(30).minutes.do(scheduleAllSpiders).tag("recheck-task")

def list_jobs():
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("================= "+curr_time+" =================")
    print("- Running Schedules: ")
    print(schedule.jobs)
    print("- Running Schedules on Server: ")
    try:
        r = requests.get(api_url + 'listprojects.json')
        projects = r.json()

        for project in projects['projects']:
            print(" === "+project+" ===")
            r = requests.get(api_url + 'listjobs.json', params = { 'project':project })
            jobs = r.json()
            print("+ Pending Jobs:")
            for pending_jobs in jobs['pending']:
                print(" |_ "+pending_jobs['spider']+" ("+ pending_jobs['id']+")")

            print("+ Completed Jobs:")
            for completed_jobs in jobs['finished']:
                print(" |_ "+completed_jobs['spider']+" ("+ completed_jobs['id']+") ")
                print("      START: "+completed_jobs['start_time']+" END: "+completed_jobs['end_time'])

            print("+ Running Jobs:")
            for running_jobs in jobs['running']:
                print(" |_ "+running_jobs['spider']+" ("+running_jobs['id']+") START: "+running_jobs['start_time'])
    except Exception as e:
        logger.error(str(e))
        print("Error:" +str(e))

def scheduleAllSpiders():
    logger.debug("Started Scheduler")
    schedule.clear("daily-task")
    schedule.clear("recheck-task")
    r = requests.get(api_url + 'daemonstatus.json')
    if r.status_code != 200:
        logger.error("Status Code (deamonstatus.json): "+str(r.status_code))
        exit()
    try:
        response = r.json()
        logger.debug("Received Response: "+str(response))
        if response['running'] == 0 and response['pending'] == 0:
            scheduleScheduler()
            p = requests.get(api_url + "listprojects.json")
            if p.status_code !=200:
                 logger.error("Status Code (listprojects.json): "+str(p.status_code))
                 exit()
            data = p.json()
            logger.debug("Received Response: "+str(data))
            for project in data['projects']:
                s = requests.get(api_url + "listspiders.json", params={"project":project})
                if s.status_code != 200:
                    logger.error("Status Code (listspiders.json?project="+project+") :"+str(s.status_code)) 
                spiders = s.json()
                logger.debug("Received Response: "+str(spiders))
                for spider in spiders['spiders']:
                    payload = {"project":project, "spider":spider}
                    sch = requests.post(api_url + "schedule.json", data=payload)
                    if sch.status_code == 200:
                        job = sch.json()
	    	        logger.info("Successfully Scheduled Spider "+spider+ " JOBID: "+job['jobid'])
                    else:
		        logger.error("Status Code (schedule.json <payload> "+str(payload)+"): "+str(sch.status_code))
                        logger.error("Unable to Schedule Spider "+spider)
        else:
            logger.info("Pending Spider Jobs! ReScheduling The Check")
            scheduleRechecking()
    except Exception as e:
        logger.error("Unhandled Exception: "+str(e))
        scheduleRechecking()
    list_jobs()

scheduleScheduler()
schedule.every(1).hours.do(list_jobs)
print("Scheduler Running! Check Log file for details")
while True:
   schedule.run_pending()
   time.sleep(5)
