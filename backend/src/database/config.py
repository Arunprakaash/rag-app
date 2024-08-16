from consts import POSTGRES_SECTION
from utils import load_config

def db_config(section: str = POSTGRES_SECTION):
    parser = load_config()
    if parser.has_section(section):
        params = parser.items(section)
        db = {param[0]: param[1] for param in params}
    else:
        raise Exception(f'Section {section} not found in the config file')
    return db