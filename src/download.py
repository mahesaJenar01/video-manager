import os
import logging
from selenium.webdriver.common.by import By
from .wait_for_downloads import wait_for_downloads
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download(driver, download_dir):
    download_buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "item_open.font-semibold.text-sm.text-white"))
    )

    target_button = None
    for button in download_buttons:
        text_content = button.text.strip()

        if "720.mp4" in text_content:
            target_button = button
            break

    if target_button:
        logging.info(f"Found the button with '720.mp4': {target_button.text}")
        # Capture the list of files already in the download directory.
        existing_files = os.listdir(download_dir)
        target_button.click()

        downloaded_file = wait_for_downloads(download_dir, existing_files=existing_files)
        if downloaded_file:
            logging.info(f"File successfully downloaded: {downloaded_file}. Preparing to close webdriver.")
        else:
            logging.error("No file was downloaded.")
    else:
        logging.info("No button containing '720.mp4' was found.")
        return