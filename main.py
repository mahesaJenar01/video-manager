import time
import logging
import os
from src import (
    prepare_download_and_driver, 
    download, 
    process_all_videos
)

def main(urls):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    download_dir_name = "downloads"
    driver, download_dir = prepare_download_and_driver(download_dir_name)

    try:
        for url in urls:
            logging.info("Navigating to URL: %s", url)
            driver.get(url)

            # Capture current files in the download directory.
            existing_files = set(os.listdir(download_dir))

            # Trigger the download process.
            download(driver, download_dir)

            # Wait a few seconds to ensure the download completes.
            time.sleep(5)

            # Determine the newly downloaded file.
            new_files = set(os.listdir(download_dir)) - existing_files
            if new_files:
                downloaded_file = new_files.pop()
                downloaded_file_path = os.path.join(download_dir, downloaded_file)
                logging.info("Downloaded file detected: %s", downloaded_file_path)
            else:
                logging.error("No new file detected after download.")

            time.sleep(1)

    except Exception as e:
        logging.error("An error occurred during automation: %s", e)
    finally:
        logging.info("Closing Chrome webdriver after downloads.")
        driver.quit()

    # After the driver is closed, proceed to the trimming process.
    temp_trim_dir = os.path.join(os.getcwd(), "temp_trim")
    final_trim_dir = os.path.join(os.getcwd(), "trimmed_videos")
    logging.info("Starting video trimming process...")
    process_all_videos(download_dir, temp_trim_dir, final_trim_dir)

if __name__ == "__main__":
    urls = [
        "https://gofile.io/d/ENtyeI",
        "https://gofile.io/d/4WGM1Z"
    ]
    main(urls)
