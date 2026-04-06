import os
from moviepy import VideoFileClip
import whisper

SUPPORTED_FORMATS = [".mp4", ".mov", ".webm", ".mkv"]

# Video Converter

#TODO Remove entire function?? -->Video/audio paths always KNOWN (get passed in)
def find_video():
    print(f"OS LIST DIR: {[f for f in os.listdir(".")]}")
    found = [f for f in os.listdir(".") if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]

    if len(found) == 0:
        print("No video files found. Please add an mp4, mov, webm, or mkv file.")
        return None
    elif len(found) == 1:
        print(f"Found video: '{found[0]}'")
        return found[0]
    else:
        #TODO Not practical: terminal will not appear for user (Needs to be removed - check with team)
        
        print("Multiple video files found:")
        for i, f in enumerate(found):
            print(f"  [{i + 1}] {f}")
        while True:
            choice = input("Enter the number of the video to use: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(found):
                return found[int(choice) - 1]
            print("Invalid choice, please try again.")


# Audio Extractor

def extract_audio(video_path, output_audio_path):
    try:
        video_clip = VideoFileClip(video_path)
        video_clip.audio.write_audiofile(output_audio_path)
        print(f"Audio extracted and saved to {output_audio_path}")
    except Exception as e:
        print(f"An error occurred during audio extraction: {e}")


# Speech Recognition

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['segments']
