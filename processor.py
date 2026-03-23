#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import clip_video
from pathlib import Path
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#gets  absolute path of  current Python file and returns directory it’s located in

#function to load events from .json file
def load_events(events_file):

    events_file = Path(events_file)

    #make sure filepath for file exists
    if not events_file.exists():
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

def matching_video(events_file, uploads_dir="uploads"):
    events_file=Path(events_file)
    uploads_dir = BASE_DIR / uploads_dir #combines base directory with uploads directory to create full path to uploads directory

    json_stem = events_file.stem # ex: takes game_0001 from game_0001.json

    possible_extensions = [".mp4", ".mov"] #for now the two video extension types

    for ext in possible_extensions:
         video_path = uploads_dir / f"{json_stem}{ext}"
         if video_path.exists():
              return video_path
    #for loop to iterate through uploads directory to see if a video matches the json file name
    #if it does, it returns that video type
    #if not, it throws an error
    
    raise FileNotFoundError(
         f"No matching video for {events_file.name} in {uploads_dir}"
    )
     

def process_video(video_path, events_file, clips_dir="clips"):
     video_path = os.path.abspath(video_path) #absolute instead of relative path
     events_file = os.path.abspath(events_file)
     clips_dir = os.path.abspath(clips_dir)

     os.makedirs(clips_dir, exist_ok=True)
     
     events = load_events(events_file)
        #pass in the data.json file
     
     for i, event in enumerate(events):
          #enumerate loops over an iterable and keeps track of an index
          
          event_type = event["type"]
          label = event["label"]
          time = event["timestamp"]
          # if type == hit or error then it goes to a different folder
          output_path = os.path.abspath(os.path.join(clips_dir, f"{i + 1}_{label}.mp4"))
          clip_video(
            video_path=video_path, 
            start_time=time, 
            duration=8, 
            output_path=output_path
            )


video_path = os.path.join(BASE_DIR, "uploads", "video1.mp4")
events_path = os.path.join(BASE_DIR, "data.json")

process_video(video_path, events_path)
print("ts should work I hope")

os.remove(video_path)
    
    
    # video_path locates the video file
    # events_file JSON file containing timestamps
    # """
    # print("Starting video processing now....")

#get .mp4 from uploads directory
#import the json file from audio detection
#call clipper.py and pass json files values
#export generated clips to clips directory
#delete .mp4 from uploads directory after file is processed
