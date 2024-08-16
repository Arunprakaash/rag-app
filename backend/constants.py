import os

from dotenv import load_dotenv

load_dotenv()

DB_INIT_FILE = 'database.ini'

POSTGRES_SECTION = 'postgresql'

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")