import os
import json
import logging
import logging.config

from config.settings import Settings

settings: Settings = Settings()

def create_log_dir(dir: str) -> None:
    if not os.path.exists(dir):
        os.mkdir(dir)

def init_logger(name: str) -> logging:
    create_log_dir('log/')
    with open(settings.log_config_file, "r") as f:
        dict_config = json.load(f)
        dict_config["loggers"][name] = dict_config["loggers"][name]
    logging.config.dictConfig(dict_config)
    return logging.getLogger(name)
