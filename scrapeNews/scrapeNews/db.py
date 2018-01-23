import psycopg2
from scrapeNews.settings import DB_INFO
from scrapeNews.settings import logger
from psycopg2.extras import DictCursor, RealDictCursor as rdc

class postgresSQL(object):
    # postgresSQL class will be the class that has connection when the with postgresSQL
    # and all database related operations must take place here, (In favour of keeping the
    # number of connections low)

    connection = None

    create_site_table = "CREATE TABLE IF NOT EXISTS " + DB_INFO['SITE_TABLE'] + " (\
                            id INT PRIMARY KEY,\
                            site_name VARCHAR NOT NULL,\
                            site_url VARCHAR NOT NULL,\
                            spider_name VARCHAR NOT NULL UNIQUE\
                        )"
    create_news_table = "CREATE TABLE IF NOT EXISTS " + DB_INFO['NEWS_TABLE'] + " (\
                            id SERIAL PRIMARY KEY,\
                            title VARCHAR NOT NULL CHECK (title <> 'Error'),\
                            content VARCHAR NOT NULL CHECK (content <> 'Error'),\
                            link VARCHAR NOT NULL UNIQUE,\
                            image VARCHAR NOT NULL,\
                            newsDate TIMESTAMP WITHOUT TIME ZONE NOT NULL,\
                            datescraped TIMESTAMP WITHOUT TIME ZONE,\
                            site_id SMALLINT NOT NULL REFERENCES " + DB_INFO['SITE_TABLE'] + " (id) ON DELETE CASCADE,  \
                            log_id INT NOT NULL DEFAULT -1 REFERENCES " + DB_INFO['LOG_TABLE'] + " (id) ON DELETE SET DEFAULT\
                        )"
    create_logs_table = "CREATE TABLE IF NOT EXISTS " + DB_INFO['LOG_TABLE'] + " (\
                            id SERIAL PRIMARY KEY,\
                            spider_id INT NOT NULL REFERENCES " + DB_INFO['SITE_TABLE'] + " (id) ON DELETE CASCADE,\
                            process_id SMALLINT NOT NULL,\
                            start_time TIMESTAMPTZ,\
                            end_time TIMESTAMPTZ,\
                            urls_parsed SMALLINT,\
                            urls_scraped SMALLINT,\
                            urls_dropped SMALLINT,\
                            urls_stored SMALLINT,\
                            close_reason VARCHAR,\
                            job_id VARCHAR DEFAULT -1\
                        )"

    insert_site_str = "INSERT INTO " + DB_INFO['SITE_TABLE'] + " \
                       (id, site_name, site_url, spider_name) VALUES (%s, %s, %s, %s)"

    def __init__(self):
        self.connect()

    def connect(self):
        # Check if connection already exists
        if self.connection != None:
            # Is Connection Closed?
            if self.connection.closed == 0:
                # If Not, Return the current cursor
                return self.cursor
        # Create a New Connection
        try:
            # Connect to Database
            self.connection = psycopg2.connect(host= DB_INFO['HOST_NAME'],
                user=DB_INFO['USERNAME'],
                database=DB_INFO['DATABASE_NAME'],
                password=DB_INFO['PASSWORD'])
            # Enable AutoCommit
            self.connection.autocommit = True
            # Set Cursor to DictCursor
            self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            self.RealDictCursor = self.connection.cursor(cursor_factory = rdc)

            logger.debug(__name__+" Connected to Database")
            
            # Try Initializing the Database
            if not self.initilaize():
                logger.error(__name__ + " Database Cannot be initialiazed automatically. Try it Manually.")
            
            return self.cursor
        except Exception as e:
            logger.critical(__name__+" Database Connection Error! Msg: " + str(e))
            if self.connection != None:
                self.connection.close()
                self.connection = None

        return False

    def initilaize(self):
        """ Initialize the Database """
        try:
            # Check if Connection exists
            if not self.connect():
                return False
            # Create Tables
            self.cursor.execute(self.create_site_table)
            self.cursor.execute(self.create_logs_table)
            self.cursor.execute(self.create_news_table)
            #Commit
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            logger.error(__name__+" Database Initilaization Error "+str(e))
        
        return False

    def siteExists(self, site_id):
        """ Checks if Given Site Id Exists in SITE_TABLE. Returns Bool """
        try:
            # Check if connection exists
            if not self.checkConnection():
                return False
            # Prepare the Query
            sql = "SELECT spider_name FROM " + DB_INFO['SITE_TABLE'] + " WHERE id=%s LIMIT 1"
            # Execute the Query
            self.cursor.execute(sql, (site_id,))
            # Verify if site Exists
            if len(self.cursor.fetchall()) == 1:
                return True
            else:
                return False
        except Exception as e:
            logger.error(__name__ + " Unable to Verify Site with site_id " + str(site_id) + " Msg:" + str(e))

        return False

    def end_log(self, log_id, stats, reason):
        # closes connection with postgreSQL using pyscopg2
        try:
            # Prepare the Query
            command = "UPDATE " + DB_INFO['LOG_TABLE'] + " SET end_time=NOW(), urls_dropped=%s, urls_scraped=%s, urls_parsed=%s, urls_stored=%s, close_reason=%s WHERE id=%s"
            # Execute the Query
            self.cursor.execute(command,(
                stats['urls_dropped'],
                stats['urls_scraped'],
                stats['urls_parsed'],
                stats['urls_stored'],
                reason,
                log_id,
                ))
            if stats['urls_stored'] > 0:
                logger.info(__name__ + " " + str(stats['urls_stored'])  + " record(s) were added for log#" + str(log_id))
            return True
        except psycopg2.Error as Error:
            logger.error(__name__ + " Unable to end log : " + str(Error.pgcode) + " : " + str(Error))
            return False
        except Exception as Error:
            logger.error(__name__ + " [Unhandled] Error While Ending Log#" + str(log_id) + " : " + str(Error))
            return False

    def insertIntoNewsTable(self, item, log_id):
        # Insert item into NEWS_TABLE after all the processing.
        try:
            # Verify the Connection to Database
            if not self.checkConnection():
                return False
            # Prepare the Query
            postgresQuery = "INSERT INTO " + DB_INFO['NEWS_TABLE'] + " (title, content, image, link, newsDate, site_id, log_id, datescraped) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"

            # Execute the Query
            self.cursor.execute(postgresQuery,
                (item['title'],
                item['content'],
                item['image'],
                item['link'],
                item['newsDate'],
                item['source'],
                log_id))
            return True
        except psycopg2.Error as Error:
            # If the link already exists, this exception will be invoked
            if (str(Error.pgcode) == '23505'):
                pass
            else:
                logger.error(__name__ + "(" + str(Error.pgcode) + ") " + str(Error) + " occured at " + str(item.get('link')))
        except Exception as Error:
            logger.error(__name__ + " Error While Inserting to Database : " + str(Error))
        
        return False

    def checkUrlExists(self, link):
        # Check if the url already exists in the database.
        try:
            # Verify the Connection
            if not self.checkConnection():
                return False
            # Prepare the Query
            sql = "SELECT link FROM " + DB_INFO['NEWS_TABLE'] + " WHERE link= %s"
            # Execute the Query
            self.cursor.execute(sql, (link,))
            if self.cursor.rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            logger.error(__name__+" DATABASE ERROR: "+str(e))
        return False

    def start_log(self, site_id, pid):
        """ Starts the Spider Log for given Site Id """
        try:
            # Prepare the Query
            sql = "INSERT INTO " + DB_INFO['LOG_TABLE'] + " \
                    (spider_id, process_id, start_time, close_reason)\
                    VALUES (%s, %s, NOW(), 'crawling') RETURNING id"
            # Executr the Query
            self.cursor.execute(sql, (site_id, pid))

            # This will reach here only if everything was successfull
            log_id = self.cursor.fetchone()['id']

            return log_id
        except Exception as e:
            logger.error(__name__ + " Unable to start log for site " + str(site_id) + " with pid " + pid + " Msg: " + str(e))
        
        return False
    
    def checkConnection(self):
        """ Checks Connection to Database, Attempts to reconnect it if closed """
        try:
            # Start The connection if not already
            if self.connection == None:
                logger.error(__name__+ " Connection is not established. Connecting Now...")
                self.connect()
                # Verify if connected
                return self.checkConnection()
            # Check if Connection was initialized but closed
            elif self.connection.closed != 0:
                logger.error(__name__ + " Closed Connection Detected. Trying to reconnect...")
                self.reconnect()
                # Verify if connected
                return self.checkConnection()
            # All Ok!
            else:
                return True
        except NameError as e:
            logger.error(__name__ + " Unable to start a closed database connection! Msg: " +str(e))
            return False
        except Exception as e:
            logger.error(__name__+" [Unhandled] Unable to start a closed database connection : " + str(e) )
        return False

    def reconnect(self):
        """ Reconnects a closed database connection """
        max_tries = 3
        curr_tries = 0
        logger.error(__name__ + " Trying to reconnect to database ")
        while curr_tries < max_tries:
            curr_tries += 1
            if self.connection != None:
                if self.connection.closed == 0:
                    break
            logger.error(__name__ + " Trying to reconnect to Database " + str(curr_tries) + "/" + str(max_tries))
            self.connect()
        # Verify if reconnection was successfull
        if self.connection == None or self.connection.closed != 0:
            return False
        else:
            return True

def createDatabase():
    # This function is creating the database, it is different that others because it uses a
    # different connection (because you cannot create a database while on it, duh!)
    # It can be called anytime to create the database and is called automatically when scrapy crawls
    try: 
        connection = psycopg2.connect(
            host= DB_INFO['HOST_NAME'],
            user=DB_INFO['USERNAME'],
            database='postgres',
            password=DB_INFO['PASSWORD'])
        cursor = connection.cursor()
        connection.autocommit = True
        postgresCommand = 'CREATE DATABASE ' + DB_INFO['DATABASE_NAME']
        cursor.execute(postgresCommand)
        cursor.close()
        connection.close()
    except psycopg2.ProgrammingError as Error:
        pass
    except psycopg2.Error as Error:
        logger.error(__name__ + " Error in Database Creation: " + str(Error.pgcode) +  " : " + str(Error))
    except Exception as Error:
        logger.error(__name__ + " [Unhandled] Error in Database Creation: " + str(Error))

