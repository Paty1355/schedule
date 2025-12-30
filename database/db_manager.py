import psycopg2
from psycopg2 import sql

class DBManager:
    def __init__(self, conn_params):
        """initializes the database manager"""
        try:
            self.conn = psycopg2.connect(**conn_params)
            self.cur = self.conn.cursor()
            #print("Connected to the database")
        except Exception as e:
            #print(f"Database connection error: {e}")
            raise
    
    def close(self):
        """closes the connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        #print("Closed database connection")
    
    def __del__(self):
        """destructor - closes the connection when the object is deleted"""
        try:
            self.close()
        except:
            pass