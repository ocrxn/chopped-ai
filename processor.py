#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import clip_video
from pathlib import Path
import json
import os
import random

BASE_DIR = Path(__file__).resolve().parent
#gets absolute path of current Python file and returns directory it’s located in; makes BASE_DIR a path
#__file__ is the path to the current Python file
#.resolve turns it into an absolute path
#.parent gets the folder containing the file

#function to load events from .json file
def load_events(events_file):

    events_file = Path(events_file)

    #make sure filepath for file exists
    if not events_file.exists():
        raise Exception("file does not exist")

    # Open JSON file with exceptions
    try:
        # load JSON data in read mode
        with open(events_file, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
            raise Exception("Events JSON is not valid JSON")
            
    # check to make sure it's a list
    if not isinstance(data, list):
        raise Exception("Events JSON must be a list")
    
    return data

def matching_video(events_file, uploads_dir="uploads"): #debugged
    events_file=Path(events_file)
    uploads_dir = BASE_DIR / uploads_dir #combines base directory with uploads directory to create full path to uploads directory

    json_stem = events_file.stem # ex: takes game_0001 from game_0001.json

    possible_extensions = [".mp4", ".mov", ".webm", ".mkv"]
    print(json_stem)
    for ext in possible_extensions:
         video_path = uploads_dir / f"{json_stem}{ext}"
         if video_path.exists():
              return video_path
    #for loop to iterate through uploads directory to see if a video matches  json file name
    
    raise FileNotFoundError(
         f"No matching video for {events_file.name} in {uploads_dir}"
    )

def process_video(events_file, clips_dir = "clips"):
     events_file = Path(events_file).resolve()
     clips_dir = Path(clips_dir).resolve()

     #match json file to video file
     video_path = matching_video(events_file)

     os.makedirs(clips_dir, exist_ok=True)
     events = load_events(events_file)
     #pass in data from json file
     
     folder_map = {
               #key -> value; dictionary to compare Python file to
               "hit": "hits",
               "out": "outs",
               "error": "errors",
               "bunt": "bunts",
               "pickoff": "pickoffs"
          }
     
     for i, event in enumerate(events):
        #loops through event in events but also keeps track of index i
                    
        event_type = event["type"]
        label = event["label"]
        time = event["timestamp"]
        num = random.randint(1000, 9999)

        folder_name = folder_map[event_type]
        #folder_map(event_type) means event type "hit" gives "hits"

        new_clips_dir = clips_dir / folder_name
        os.makedirs(new_clips_dir, exist_ok=True)

        output_path = new_clips_dir / f"{label}_{i+num}{video_path.suffix}"

        clip_video(
                 video_path=video_path, 
                 start_time= max(0, time - 8), 
                 duration=20, 
                 output_path=output_path
                 )
    
            #os.remove(video_path)

json_dir = BASE_DIR / "json"

for json_file in json_dir.glob("*.json"):
    #glob says must start with game_, * is a wildcard, and must end with .json (or whatever the filename is)

    try:
        game_clips_dir = BASE_DIR / "clips" / json_file.stem
        process_video(json_file, clips_dir = game_clips_dir)
            #process_video will make a new directory within the clips folder
            #it will have the name of json_file.stem
    except Exception as e:
        print(f"Error processing {json_file.name}: {e}")
    #if error happens in try block, store in variable e, and print that error as a message

print("Success: check clips folder")
