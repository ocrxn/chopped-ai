#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import cut_clip
from pathlib import Path
import json
import os

#function to load events from .json file
def load_events(events_file):

    events_file = Path(events_file)

    if not events_file.exists:
        raise Exception("file does not exist")

    # Open JSON file with exceptions
    try:
        with open(events_file, 'r') as file:
            # load JSON data
            data = json.load(file)
    except json.JSONDecodeError:
            raise Exception("Events JSON is not valid JSON")
            
    # check to make sure it's a list
    if not isinstance(data, list):
        raise Exception("Events JSON must be a list")
    
    return data
        


def process_video(video_path: str, events_file: str):
    video_path = Path(video_path)

    events = load_events(events_file)

    """
    video_path locates the video file
    events_file JSON file containing timestamps
    """
    print("Starting video processing now....")

#get .mp4 from uploads directory
#import the json file from audio detection
#call clipper.py and pass json files values
#export generated clips to clips directory
#delete .mp4 from uploads directory after file is processed