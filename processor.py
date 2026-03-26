#takes timestamps + labels and decides where clips start and end
#calls clipper.py to generate all clips

from clipper import clip_video
from pathlib import Path
import json
import os

BASE_DIR = Path(__file__).resolve().parent
#gets absolute path of current Python file and returns directory it’s located in; makes BASE_DIR a path
#__file__ is the path to the current Python file
#.resolve turns it into an absolute path
#.parent gets the folder containing the file
#overall gets the absolute path to the folder where the file is

#function to load events from .json file
def load_events(events_file): #debugged

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

def matching_video(events_file, uploads_dir="uploads"): #debugged
    events_file=Path(events_file)
    uploads_dir = BASE_DIR / uploads_dir #combines base directory with uploads directory to create full path to uploads directory

    json_stem = events_file.stem # ex: takes game_0001 from game_0001.json

    possible_extensions = [".mp4", ".mov", ".webm", ".mkv"] #for now the two video extension types
    print(json_stem)
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
     

def process_video(events_file, clips_dir = "clips"): #not debugged
     events_file = Path(events_file).resolve()
     clips_dir = Path(clips_dir).resolve()
     #needs to loop through JSON file and uploads folder
     video_path = matching_video(events_file)

     os.makedirs(clips_dir, exist_ok=True)
     
     events = load_events(events_file)
        #pass in the data.json file
     
     for i, event in enumerate(events):
          #enumerate loops over an iterable and keeps track of an index
          
          event_type = event["type"]
          label = event["label"]
          time = event["timestamp"]
          # if type == hit or error then it goes to a different folder
          if event_type == "hit":
            new_clips_dir = clips_dir / "hits"
            os.makedirs(new_clips_dir, exist_ok=True) #exist_ok=True prevents raising an error if target directory already exists
            output_path = new_clips_dir / f"{i + 1}_{label}.mp4" #has to be clips_dir
            clip_video(
                video_path=video_path, 
                start_time= time, 
                duration=8, 
                output_path=output_path
                )
          elif event_type == "error":
            new_clips_dir = clips_dir / "errors"
            os.makedirs(new_clips_dir, exist_ok=True)
            output_path = new_clips_dir / f"{i + 1}_{label}.mp4"
            clip_video(
                video_path=video_path, 
                start_time= time,
                duration=8, 
                output_path=output_path
                )

#loop that calls matching_video and then passes that into process_video
#opens the json folder



#video = os.path.join(BASE_DIR, "uploads", "game_0001.mp4")
#json = os.path.join(BASE_DIR, "game_0001.json")

json_dir = BASE_DIR / "json"

for json_file in json_dir.glob("game_*.json"): #glob automatically handes game_0001.json, game_0002.json, game_0003.json, etc.
    #glob works if files are missing; will skip 2 if 2 is not there
    #glob says must start with game_, * is a wildcard, and must end with .json
    try:
        game_clips_dir = BASE_DIR / "clips" / json_file.stem
        process_video(json_file, clips_dir = game_clips_dir)
            #process_video will make a new directory within the clips folder
            #it will have the name of json_file.stem (game_0001, game_0002, etc.)
    except Exception as e:
        print(f"Error processing {json_file.name}: {e}")
    #if error happens in try block, store in variable e, and print that error as a message

print("Success: check clips folder")

#os.remove(video_path)
    
    
    # video_path locates the video file
    # events_file JSON file containing timestamps
    # """
    # print("Starting video processing now....")

#get .mp4 from uploads directory: good
#import the json file from audio detection: good
#call clipper.py and pass json files values: good
#export generated clips to clips directory: good
#delete .mp4 from uploads directory after file is processed: good
#call matching_video in relation to process_video
