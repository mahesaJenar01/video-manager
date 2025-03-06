import os
import random
import logging
import subprocess
from moviepy import VideoFileClip
from .move_trimmed import move_trimmed

def reencode_subclip_ffmpeg(
    input_video, start_time, end_time, output_video
):
    """
    Calls ffmpeg via subprocess to re-encode the subclip from start_time to end_time.
    """
    # This command re-encodes with h264 video and aac audio
    # -ss tells ffmpeg when to start
    # -to tells ffmpeg when to stop
    # -map 0 copies all streams from the input (though you can refine if needed)
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output if it exists
        "-i", input_video,
        "-ss", str(start_time),
        "-to", str(end_time),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-map", "0",
        output_video
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def trim_video(video_path):
    logging.info(f"Starting trimming for video: {video_path}")

    try:
        clip = VideoFileClip(video_path)
        video_duration = clip.duration
        clip.close()
    except Exception as e:
        logging.error(f"Error loading video {video_path}: {e}")
        return

    logging.info(f"Video duration: {video_duration:.2f} seconds")
    current_start = 0
    trimmed_files = []
    original_filename = os.path.basename(video_path)
    file_root, ext = os.path.splitext(original_filename)

    for i in range(4):
        # random 3-5 minute segment
        random_duration_minutes = round(random.uniform(3, 5), 2)
        random_duration_seconds = random_duration_minutes * 60
        end_time = current_start + random_duration_seconds

        if end_time > video_duration:
            end_time = video_duration
        if current_start >= video_duration:
            logging.info("No more video left to trim.")
            break

        trimmed_filename = f"{file_root}_trim_{i+1}{ext}"
        try:
            logging.info(f"Trimming segment {i+1}: {current_start:.2f} to {end_time:.2f}")
            reencode_subclip_ffmpeg(video_path, current_start, end_time, trimmed_filename)
            trimmed_files.append(trimmed_filename)
        except Exception as e:
            logging.error(f"Error trimming segment {i+1}: {e}")

        # Prepare for the next subclip
        current_start = end_time + 1
        if current_start >= video_duration:
            logging.info("Reached the end of the video.")
            break

    # Move trimmed files into their own folder
    for trimmed_file in trimmed_files:
        try:
            move_trimmed(trimmed_file, original_filename)
            logging.info(f"Moved trimmed file {trimmed_file} successfully.")
        except Exception as e:
            logging.error(f"Error moving trimmed file {trimmed_file}: {e}")
