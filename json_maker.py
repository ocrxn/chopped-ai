import os
import json
from json_utilities import find_video, extract_audio, transcribe_audio
from config import UPLOAD_FOLDER

# Map each phrase to its type and label for the JSON output
trigger_phrases = {
    "double play": {"type": "hit", "label": "Double Play"},
    "strikeout": {"type": "out", "label": "Strikeout"},
    "groundout": {"type": "out", "label": "Groundout"},
    "flyout": {"type": "out", "label": "Flyout"},
    "pickoff": {"type": "pickoff", "label": "Pickoff"},
    "bunt": {"type": "bunt", "label": "Bunt"},
    "single": {"type": "hit", "label": "Single"},
    "double": {"type": "hit", "label": "Double"},
    "triple": {"type": "hit", "label": "Triple"},
    "home run": {"type": "hit", "label": "Home Run"},
    # Positional errors E1-E9
    "e1": {"type": "error", "label": "E1"},
    "e2": {"type": "error", "label": "E2"},
    "e3": {"type": "error", "label": "E3"},
    "e4": {"type": "error", "label": "E4"},
    "e5": {"type": "error", "label": "E5"},
    "e6": {"type": "error", "label": "E6"},
    "e7": {"type": "error", "label": "E7"},
    "e8": {"type": "error", "label": "E8"},
    "e9": {"type": "error", "label": "E9"},
    "error": {"type": "error", "label": "Error"},
}

# Sort longest first so "double play" is matched before "double"
sorted_phrases = sorted(trigger_phrases.keys(), key=len, reverse=True)


def find_trigger_segments(segments):
    matches = []
    for segment in segments:
        text_lower = segment['text'].lower()
        for phrase in sorted_phrases:
            if phrase in text_lower:
                matches.append({
                    "type": trigger_phrases[phrase]["type"],
                    "timestamp": round(segment['start']),
                    "label": trigger_phrases[phrase]["label"]
                })
                break
    return matches


def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted {path}")
    except PermissionError:
        print(f"Could not delete {path} — you can delete it manually.")


def create_json_file(video_path,audio_path,video_name):
    # Extract audio if separate audio not provided
    if audio_path == None:
        audio_path = f"{video_name}.wav"
        extract_audio(video_path, audio_path)

    # Transcribe audio
    segments = transcribe_audio(audio_path)

    if not segments:
        print("No transcription available.")
        return

    print(f"Transcription complete. {len(segments)} segments found.")

    # Search for trigger phrases and build JSON output
    matches = find_trigger_segments(segments)
    if not matches:
        print("No trigger phrases found in transcript.")
        return

    # Write results to JSON file
    output_path = os.path.join(UPLOAD_FOLDER, f"{video_name}.json")
    with open(output_path, "w") as f:
        json.dump(matches, f, indent=4)
    print(f"\nDetected {len(matches)} voiceline(s). Saved to {output_path}")

    # Delete the audio file
    delete_file(audio_path)
