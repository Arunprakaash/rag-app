import psycopg2
from configparser import ConfigParser
from fastapi import HTTPException
from pathlib import Path

from constants import DB_INIT_FILE, POSTGRES_SECTION

def db_config(filename: Path = DB_INIT_FILE, section: str = POSTGRES_SECTION):
    print(filename)
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        params = parser.items(section)
        db = {param[0]: param[1] for param in params}
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db

def get_db_connection():
    params = db_config()
    try:
        params['host'] = 'db'
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        raise HTTPException(status_code=500, detail="Database connection error")