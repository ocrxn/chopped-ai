#cuts a highlight clip from a video
#uses FFmpeg when given a video path and timestamps

from __future__ import annotations

import subprocess #lets Python run other programs on computer (FFmpeg)
from pathlib import Path #necessary for working with folders
import json

events_file = Path('/Users/matth/Documents/Innovation-Scholars/baseball-highlights-chopclips/backend/chopped-ai/data.json')

    # Open JSON file
if events_file.exists():
    with open(events_file, 'r') as file:
    # load JSON data
        data = json.load(file)
        print(data)
else:
    #print if json file is not open
        print("JSON file not found")

def clip_video(video_path: str, type: str, time: int, duration: 35):
     