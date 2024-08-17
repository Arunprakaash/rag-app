import psycopg2
from fastapi import HTTPException

from .config import db_config


def get_db_connection():
    params = db_config()
    try:
        params['host'] = 'db'
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        raise HTTPException(status_code=500, detail="Database connection error")
