import psycopg2
from config import *

# Connect to database
try:
    conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s"
                            % (db_name, db_host, db_user, db_password))
    print(conn)
except:
    print ("Unable to connect to database: " + db_name)

# Use Autocommit mode for database connection
conn.set_isolation_level(0)
cursor = conn.cursor()

cursor.execute("""DROP TABLE IF EXISTS urls, slds, campaigns,
        domains_seen, gsb
        """)
print ("""Dropped the tables:
        urls, slds, campaigns, domains_seen, gsb
        """)
cursor.execute("DROP TYPE IF EXISTS url_type")

cursor.close()
conn.close()
