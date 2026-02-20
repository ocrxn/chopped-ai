#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import cut_clip
from pathlib import Path
import json

def process_video(video_path: str, events_file: str):
    """
    video_path locates the video file
    events_file JSON file containing timestamps
    """
    print("Starting video processing now....")

