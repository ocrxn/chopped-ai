import os
import time
from moviepy import VideoFileClip
import whisper

SUPPORTED_FORMATS = [".mp4", ".mov", ".avi", ".mkv"]

# Video Converter

def find_and_convert_video(output_filename="video.mp4"):
    if os.path.exists(output_filename):
        print("Found existing video.mp4, using it directly.")
        return "video"

    found = [f for f in os.listdir(".") if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]

    if len(found) == 0:
        print("No video files found. Please add an mp4, mov, avi, or mkv file.")
        return None
    elif len(found) == 1:
        input_filename = found[0]
    else:
        print("Multiple video files found:")
        for i, f in enumerate(found):
            print(f"  [{i + 1}] {f}")
        while True:
            choice = input("Enter the number of the video to use: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(found):
                input_filename = found[int(choice) - 1]
                break
            print("Invalid choice, please try again.")

    original_name = os.path.splitext(input_filename)[0]

    for attempt in range(10):
        try:
            os.rename(input_filename, output_filename)
            print(f"'{input_filename}' renamed to '{output_filename}'")
            return original_name
        except PermissionError:
            print(f"File is in use, retrying in 3 seconds... ({attempt + 1}/10)")
            time.sleep(3)

    print(f"Could not rename '{input_filename}' — make sure it isn't open in another program.")
    return None

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




