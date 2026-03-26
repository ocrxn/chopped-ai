#cuts a highlight clip from a video
#uses FFmpeg when given a video path and timestamps

from __future__ import annotations

import subprocess #lets Python run other programs on computer (FFmpeg)
from pathlib import Path #necessary for working with file paths
import json
import os



def clip_video(video_path: str, output_path: str, start_time: int, duration: int = 35):
    video_path = os.path.abspath(video_path)
    output_path = os.path.abspath(output_path)

    if not os.path.exists(video_path):
        raise FileNotFoundError("input video not found: {video_path}")
    command = [
        "ffmpeg",
        "-ss", str(start_time), #start cutting at start time
        "-i", video_path, #input video file
        "-t", str(duration), #duration of the cut
        "-c", "copy", #copies audio and video streams without re-encoding
                      #makes process faster
        "-y", #so ffmpeg won't stop if file already exists
        output_path #output path for cut video file
    ]

    subprocess.run(command, check=True)

#takes in video file path
#takes in data from JSON file from processor.py
#uses JSON parameters
#uses ffmpeg to cut clips and put into folders