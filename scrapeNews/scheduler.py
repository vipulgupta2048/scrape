import logging
import os
import time

import requests
import schedule

from datetime import datetime
from time import strftime

# Scrapyd Server Url
api_url = "http://localhost:6800/"

# Custom Logging Configuration
logger = logging.getLogger("scraperScheduler")
handler = logging.FileHandler('logs/scraperScheduler.log')
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def scheduleScheduler():
    """ Schedules Daily Task """
    schedule.every().day.at("00:00").do(scheduleAllSpiders).tag("daily-task")

def scheduleRechecking():
    """ Schedules Rechecking every 30 mins incase of pending tasks or errors """
    schedule.clear("daily-task")
    schedule.every(30).minutes.do(scheduleAllSpiders).tag("recheck-task")

def list_jobs():
    """List jobs in a user-friends manner
    
    This method should only be used when the script is not being used as a service.
    
    """

    # Clear the console
    os.system('clear')

    # Get Current Time
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Print Header
    print("++++++++ Scrapyd Scheduler (thisisayush) ++++++++")
    print("================= "+curr_time+" =================")
    print(" [ CHECK LOG FILE FOR ERRORS ] [PID: " + str(os.getpid()) + "]")
    print("- Running Schedules: (Updated Every 1 minute)")

    # Print Current Schedules
    print(schedule.jobs)

    # Start Printing Schedules on Scrapyd Server
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
        logger.error(__name__ + " [UNHANDLED] " + str(e))
        print("Error:" +str(e))

def scheduleAllSpiders():
    """ Schedules All Spiders on Scrapyd Server """

    logger.debug(__name__ + " Scheduling Jobs (PID: " + str(os.getpid()))

    # Clear any previous schedules
    schedule.clear("daily-task")
    schedule.clear("recheck-task")

    # Get current job status from scrapyd server
    r = requests.get(api_url + 'daemonstatus.json')
    if r.status_code != 200:
        # Schedule Rechecking incase of NON-200 Response
        logger.error(__name__ + " Recieved Status Code (deamonstatus.json): " + str(r.status_code))
        scheduleRechecking()
        return
    try:
        # Parse Response
        response = r.json()
        logger.debug(__name__ + " Received Response: " + str(response))
        
        # Check for running or pending jobs
        if response['running'] == 0 and response['pending'] == 0:
            scheduleScheduler()

            # Get Projects Deployed 
            p = requests.get(api_url + "listprojects.json")
            
            if p.status_code !=200:
                 logger.error(__name__ + " Received Status Code (listprojects.json): "+ str(p.status_code))
                 scheduleRechecking()
                 return

            # Parse Response
            data = p.json()

            # Fetch Deployed Spiders for each project
            for project in data['projects']:
                # Get Spiders for project
                s = requests.get(api_url + "listspiders.json", params={"project":project})
                if s.status_code != 200:
                    logger.error(__name__ + " Received Status Code (listspiders.json?project="+project+") :" + str(s.status_code))
                    return

                # Parse Response
                spiders = s.json()

                # Schedule Each Spider for project
                for spider in spiders['spiders']:
                    # Create a payload
                    payload = {"project":project, "spider":spider}

                    # Send The Request
                    sch = requests.post(api_url + "schedule.json", data=payload)
                    
                    if sch.status_code == 200:
                        # Parse Response
                        job = sch.json()
                        logger.info(__name__ + " Successfully Scheduled Spider " + spider + " JOBID: " + job['jobid'])
                    else:
                        logger.error(__name__ + " Received Status Code (schedule.json <payload> " + str(payload) + "): " + str(sch.status_code))
                        logger.error(__name__ + " Unable to Schedule Spider " + spider)
        else:
            logger.info(__name__ + " There are jobs pending! Rescheduling Check!")
            scheduleRechecking()
    except Exception as e:
        logger.error(__name__ + " [UNHANDLED] : " + str(e))
        logger.info(__name__ + " Recheck Scheduled")
        scheduleRechecking()

scheduleScheduler()

while True:
   schedule.run_pending()
   time.sleep(5)