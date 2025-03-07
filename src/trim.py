import os
import cv2
import random
import logging
import multiprocessing
from .move_trimmed import move_trimmed_file

def get_video_duration(video_path):
    """Get duration of video in seconds using OpenCV."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Error opening video file: %s", video_path)
        return 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    logging.info("Video '%s' duration: %.2f seconds", video_path, duration)
    return duration

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}"

def trim_video(input_path, output_path, start_time, end_time):
    """Trim a video segment from start_time to end_time using OpenCV."""
    logging.info("Starting trimming for '%s' from %s to %s", input_path, format_time(start_time), format_time(end_time))
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        logging.error("Error opening video file: %s", input_path)
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Use XVID codec for faster processing
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Calculate start and end frames
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frame_count = 0
    max_frames = end_frame - start_frame

    while True:
        ret, frame = cap.read()
        if not ret or frame_count >= max_frames:
            break

        out.write(frame)
        frame_count += 1

        if frame_count % 300 == 0:
            logging.info("Processed %d/%d frames for '%s'", frame_count, max_frames, input_path)

    cap.release()
    out.release()
    logging.info("Completed trimming segment, saved to '%s'", output_path)
    return True

def process_video(video_path, temp_trim_dir, final_trim_dir):
    """
    Process a single video:
    - Create a temporary folder for trimmed segments.
    - Trim the video into multiple segments (random lengths between 3-5 minutes).
    - Move each trimmed segment to the final trimmed videos directory using move_trimmed_file.
    """
    filename = os.path.basename(video_path)
    video_name = os.path.splitext(filename)[0]
    video_temp_folder = os.path.join(temp_trim_dir, video_name)

    if not os.path.exists(video_temp_folder):
        os.makedirs(video_temp_folder)
        logging.info("Created temporary folder for '%s' at '%s'", video_name, video_temp_folder)

    duration = get_video_duration(video_path)
    if duration <= 0:
        logging.error("Skipping '%s' - could not determine duration.", filename)
        return

    logging.info("Processing video '%s' (duration: %s)", filename, format_time(duration))

    # Use a maximum working duration of 24 minutes (if video is longer)
    working_duration = min(duration, 24 * 60)
    current_time = 0

    for i in range(4):  # Create 4 trimmed segments
        trim_length = random.randint(3 * 60, 5 * 60)  # Random trim length in seconds
        end_time = min(current_time + trim_length, working_duration)

        if end_time <= current_time:
            logging.info("Skipping trim %d for '%s' - reached end of video", i + 1, filename)
            break

        temp_output_filename = f"{video_name}_trim{i+1}.mp4"
        temp_output_path = os.path.join(video_temp_folder, temp_output_filename)

        logging.info("Trimming segment %d for '%s': %s to %s", i + 1, filename, format_time(current_time), format_time(end_time))
        success = trim_video(video_path, temp_output_path, current_time, end_time)
        if success:
            logging.info("Successfully created trimmed segment '%s'", temp_output_filename)
            # Move the trimmed segment to the final destination
            move_trimmed_file(temp_output_path, final_trim_dir)
        else:
            logging.error("Failed to create trimmed segment '%s'", temp_output_filename)

        current_time = end_time
        if current_time >= working_duration:
            logging.info("Reached end of working duration for '%s' after %d trims", filename, i + 1)
            break

    logging.info("Completed processing video '%s'", filename)

def process_all_videos(downloads_dir, temp_trim_dir, final_trim_dir):
    """
    Process all video files in the downloads directory using multiprocessing:
    - Identifies video files by extension.
    - Processes each video concurrently using process_video.
    """
    if not os.path.exists(temp_trim_dir):
        os.makedirs(temp_trim_dir)
        logging.info("Created temporary trimming directory at '%s'", temp_trim_dir)
    if not os.path.exists(final_trim_dir):
        os.makedirs(final_trim_dir)
        logging.info("Created final trimmed videos directory at '%s'", final_trim_dir)

    video_files = [os.path.join(downloads_dir, f) for f in os.listdir(downloads_dir)
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        logging.info("No video files found in '%s' for trimming.", downloads_dir)
        return

    logging.info("Starting processing of %d video(s) for trimming.", len(video_files))

    # Determine the number of worker processes (use CPU count or number of videos, whichever is lower)
    pool_size = min(len(video_files), multiprocessing.cpu_count())

    # Use Pool.starmap to run process_video concurrently for each video file.
    with multiprocessing.Pool(processes=pool_size) as pool:
        # Prepare arguments for each video: (video_path, temp_trim_dir, final_trim_dir)
        pool.starmap(process_video, [(video_path, temp_trim_dir, final_trim_dir) for video_path in video_files])

    logging.info("Completed processing all videos for trimming.")
