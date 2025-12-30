import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

conn_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432))
}


def create_database_if_not_exists(conn_params, dbname):
    temp_params = conn_params.copy()
    temp_params['dbname'] = 'postgres'
    conn = psycopg2.connect(**temp_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"Database '{dbname}' has been created.")
    else:
        print(f"Database '{dbname}' already exists.")
    cur.close()
    conn.close()


def check_schema_exists(db_manager):
    try:
        db_manager.cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'departments'
            );
        """)
        return db_manager.cur.fetchone()[0]
    except Exception:
        return False


def run_sql_file(conn_params, filepath):
    """executes a SQL file"""    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        cur.execute(sql_commands)
        conn.commit()
        
        print(f"Executed SQL file: {filepath}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error while executing SQL file: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise