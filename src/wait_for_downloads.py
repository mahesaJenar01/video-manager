import os
import time
import logging

def wait_for_downloads(directory, timeout=60, existing_files=None):
    logging.info("Waiting for file download to complete...")
    if existing_files is None:
        existing_files = set(os.listdir(directory))
    else:
        existing_files = set(existing_files)
    end_time = time.time() + timeout

    while time.time() < end_time:
        files = os.listdir(directory)
        new_files = set(files) - existing_files
        completed_files = [f for f in new_files if not f.endswith(".crdownload") and not f.endswith(".tmp")]

        if completed_files:
            logging.info(f"File {completed_files[0]} downloaded successfully.")
            return completed_files[0]  # Return the first fully downloaded new file
        time.sleep(2)

    logging.error("Download did not complete within the expected time.")
    return None
