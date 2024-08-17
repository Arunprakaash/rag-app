import os
import configparser

from consts import DB_INIT_FILE, CONFIG


def load_config(config_file=DB_INIT_FILE):
    config = configparser.ConfigParser()
    config_path = os.path.join(CONFIG, config_file)
    config.read(config_path)
    return config
