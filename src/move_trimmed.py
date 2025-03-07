import os
import shutil
import logging

def move_trimmed_file(source_path, final_trim_dir):
    """
    Move a trimmed video file from source_path to the final_trim_dir.
    The file is organized into a subfolder named after the original video's base name.
    """
    if not os.path.exists(source_path):
        logging.error("Source file '%s' does not exist. Cannot move.", source_path)
        return False

    # Determine the video base name (assumes file is named like video_trimX.mp4)
    base_name = os.path.basename(source_path)
    video_name = base_name.split('_trim')[0]
    destination_folder = os.path.join(final_trim_dir, video_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logging.info("Created destination folder for '%s' at '%s'", video_name, destination_folder)

    destination_path = os.path.join(destination_folder, base_name)

    try:
        shutil.move(source_path, destination_path)
        logging.info("Moved file '%s' to '%s'", source_path, destination_path)
        return True
    except Exception as e:
        logging.error("Error moving file '%s' to '%s': %s", source_path, destination_path, str(e))
        return False
