import os
import time
import threading
from moviepy.editor import VideoFileClip
import whisper

SUPPORTED_FORMATS = [".mp4", ".mov", ".avi", ".mkv"]

# Video Converter

def find_and_convert_video(output_filename="video.mp4"):
    if os.path.exists(output_filename):
        print("Found existing video.mp4, using it directly.")
        return True

    found = [f for f in os.listdir(".") if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]

    if len(found) == 0:
        print("No video files found. Please add an mp4, mov, avi, or mkv file.")
        return False
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

    for attempt in range(10):
        try:
            os.rename(input_filename, output_filename)
            print(f"'{input_filename}' renamed to '{output_filename}'")
            return True
        except PermissionError:
            print(f"File is in use, retrying in 3 seconds... ({attempt + 1}/10)")
            time.sleep(3)

    print(f"Could not rename '{input_filename}' — make sure it isn't open in another program.")
    return False


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

# Progress Tracker

class ProgressTracker:
    def __init__(self):
        self.stage_start = None
        self.total_start = time.time()
        self._timer_thread = None
        self._running = False
        self.estimates = {
            "Extracting audio": 30,
            "Transcribing audio": 120,
            "Creating clip": 20,
        }

    def start_stage(self, stage_name):
        self._stop_timer()
        self.current_stage = stage_name
        self.stage_start = time.time()
        estimate = self.estimates.get(stage_name, 60)
        print(f"\n--- {stage_name} (estimated {estimate}s) ---")
        self._running = True
        self._timer_thread = threading.Thread(target=self._display_loop, args=(estimate,), daemon=True)
        self._timer_thread.start()

    def finish_stage(self):
        self._stop_timer()
        elapsed = time.time() - self.stage_start
        print(f"\n✓ Done in {elapsed:.1f}s")

    def finish_all(self):
        self._stop_timer()
        total = time.time() - self.total_start
        mins, secs = divmod(int(total), 60)
        print(f"\n=============================")
        print(f"  Total time: {mins}m {secs}s")
        print(f"=============================")

    def _display_loop(self, estimate):
        while self._running:
            elapsed = time.time() - self.stage_start
            remaining = max(0, estimate - elapsed)
            print(f"  Elapsed: {elapsed:.0f}s | Est. remaining: {remaining:.0f}s", end="\r")
            time.sleep(1)

    def _stop_timer(self):
        self._running = False
        if self._timer_thread:
            self._timer_thread.join(timeout=2)
            self._timer_thread = None
