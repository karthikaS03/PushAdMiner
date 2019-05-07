import psycopg2
import sys

from config import *

# Connect to database
try:
    conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s"
                            % (db_name, db_host, db_user, db_password))
    
except Exception as e:
    print ("Unable to connect to database: " + db_name)
    print(e)
    sys.exit()


print ("Successfully connected!")
cursor = conn.cursor()

cursor.execute("""
    CREATE TYPE url_type AS ENUM ('other', 'malvert', 'legit')
    """)

# domain, url_path, campaign
cursor.execute("""
    CREATE TABLE urls(url_id SERIAL, PRIMARY KEY(url_id),
            url TEXT, domain VARCHAR(512), url_path TEXT,
            class url_type, campaign VARCHAR(512), count INT)
            """)

# domain
cursor.execute("""
    CREATE TABLE slds (sld VARCHAR(512),
        domain VARCHAR(512), PRIMARY KEY(domain))
        """)

# campaign
cursor.execute("""
    CREATE TABLE campaigns (campaign VARCHAR(512), last_seen TIMESTAMP,
    PRIMARY KEY(campaign))
        """)

# domain, campaign
cursor.execute("""
    CREATE TABLE domains_seen (domain VARCHAR(512), campaign VARCHAR(512),
        first_seen TIMESTAMP, last_seen TIMESTAMP)
        """)

cursor.execute("""
    CREATE TABLE gsb (domain VARCHAR(512),
        first_query_time TIMESTAMP, first_flag BOOLEAN,
        first_se_flag BOOLEAN, first_result TEXT,
        last_query_time TIMESTAMP, last_flag BOOLEAN,
        last_se_flag BOOLEAN, last_result TEXT)
        """)

conn.commit()

cursor.close()
conn.close()
