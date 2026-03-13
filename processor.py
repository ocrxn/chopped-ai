#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import clip_video
from pathlib import Path
import json
import os


#function to load events from .json file
def load_events(events_file):

    events_file = Path(events_file)

    #make sure filepath for file exists
    if not events_file.exists():
        raise Exception("file does not exist")

    # Open JSON file with exceptions
    try:
        with open("data.json", 'r') as file:
            # load JSON data
            data = json.load(file)
    except json.JSONDecodeError:
            raise Exception("Events JSON is not valid JSON")
            
    # check to make sure it's a list
    if not isinstance(data, list):
        raise Exception("Events JSON must be a list")
    
    return data
     

def process_video(video_path, events_file, clips_dir="clips", output_dir="uploads"):
     os.makedirs(clips_dir, exist_ok=True)

     events = load_events(events_file)
        #pass in the data.json file
     
     for i, event in enumerate(events):
          #enumerate loops over an iterable and keeps track of an index
          
          event_type = event["type"]
          label = event["label"]
          time = event["timestamp"]
          
          output_path = os.path.join(clips_dir, f"{i + 1} {label}.mp4")
          clip_video(
            video_path=video_path, 
            start_time=time, 
            duration=8, 
            output_path=output_path
            )

video_path = "uploads/video.mp4"
os.remove(video_path)


process_video("uploads/video.mp4", "data.json")
print("ts should work I hope")
    
    
    # video_path locates the video file
    # events_file JSON file containing timestamps
    # """
    # print("Starting video processing now....")

#get .mp4 from uploads directory
#import the json file from audio detection
#call clipper.py and pass json files values
#export generated clips to clips directory
#delete .mp4 from uploads directory after file is processed
