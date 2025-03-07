import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_driver(download_dir):
    """
    Sets up the Chrome webdriver with the specified window size and download preferences.
    """
    logging.info("Setting up Chrome options.")
    chrome_options = Options()
    chrome_options.add_argument("window-size=150,150")
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    logging.info("Initializing Chrome webdriver.")
    driver = webdriver.Chrome(options=chrome_options)
    return driver