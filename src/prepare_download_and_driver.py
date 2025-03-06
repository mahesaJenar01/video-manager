import os
import logging
from .setup_driver import setup_driver

def prepare_download_and_driver(download_dir_name: str):
    download_dir = os.path.join(os.getcwd(), download_dir_name)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        logging.info("Created download directory at: %s", download_dir)
    else:
        logging.info("Download directory exists at: %s", download_dir)

    logging.info("Chrome webdriver started with window size 150,910.")

    return setup_driver(download_dir), download_dir