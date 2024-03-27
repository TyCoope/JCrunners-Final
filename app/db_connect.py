import pymysql
import pymysql.cursors
from flask import g

def get_db():
    if 'db' not in g or not is_connection_open(g.db):
        print("Re-establishing closed database connection.")
        g.db = pymysql.connect(
            #Database configuration
            #Configure MySQL
            host = 'bryanmarshall.com',
            user = 'uxag9ek69ngxu',
            password = 'temp@2024',
            database = 'db1xk2mxpvo9gr',
            cursorclass=pymysql.cursors.DictCursor  # Set the default cursor class to DictCursor
            # Site Ground configuration
           # host = 'jonescountyxc.com',
           # user = 'unh0rrp9wrp6f',
            #password = 'Andrew@2024',
            #database = 'dbzwp6bqvdjycw',
            #cursorclass=pymysql.cursors.DictCursor  # Set the default cursor class to DictCursor
        )
    return g.db

def is_connection_open(conn):
    try:
        conn.ping(reconnect=True)  # PyMySQL's way to check connection health
        return True
    except:
        return False

def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None and not db._closed:
        print("Closing database connection.")
        db.close()



