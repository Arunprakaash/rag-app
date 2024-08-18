import os


def db_config():
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv('POSTGRES_PORT'),
        "database": os.getenv('POSTGRES_DB'),
        "user": os.getenv('POSTGRES_USER'),
        "password": os.getenv('POSTGRES_PASSWORD'),
    }
