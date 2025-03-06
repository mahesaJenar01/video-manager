import os
import shutil
import logging

def move_trimmed(trimmed_file_path, original_video_filename, destination_root="trimmed_videos"):
    """
    Moves the given trimmed video file into a folder under 'trimmed_videos'.
    The folder is named after the original video's filename (without its extension).
    """
    video_base = os.path.splitext(original_video_filename)[0]
    destination_folder = os.path.join(destination_root, video_base)
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logging.info(f"Created directory: {destination_folder}")
    
    destination_path = os.path.join(destination_folder, os.path.basename(trimmed_file_path))
    shutil.move(trimmed_file_path, destination_path)
    logging.info(f"Moved {trimmed_file_path} to {destination_path}")
