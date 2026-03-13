import os
from utilities import find_and_convert_video, extract_audio, transcribe_audio, create_clip, ProgressTracker

trigger_phrases = sorted(
    ["single", "error", "strikeout", "flyout", "walk", "double", "double play", "triple", "groundout"],
    key=len,
    reverse=True
)


def find_trigger_segments(segments, trigger_phrases):
    matches = []
    for segment in segments:
        text_lower = segment['text'].lower()
        for phrase in trigger_phrases:
            if phrase in text_lower:
                matches.append((segment['start'], phrase))
                break
    return matches


def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted {path}")
    except PermissionError:
        print(f"Could not delete {path} — you can delete it manually.")


def main():
    tracker = ProgressTracker()

    # search for video file
    print("Searching for video file...")
    if not find_and_convert_video():
        return

    video_path = "video.mp4"
    audio_path = "audio.wav"

    # extracts audio
    tracker.start_stage("Extracting audio")
    extract_audio(video_path, audio_path)
    tracker.finish_stage()

    # transcribes audio
    tracker.start_stage("Transcribing audio")
    segments = transcribe_audio(audio_path)
    tracker.finish_stage()

    if not segments:
        print("No transcription available.")
        return

    print(f"Transcription complete. {len(segments)} segments found.")

    # searches for voicelines
    matches = find_trigger_segments(segments, trigger_phrases)
    if not matches:
        print("No trigger phrases found in transcript.")
        tracker.finish_all()
        return

    # Creates a clip for each voiceline
    phrase_counts = {}
    for (detected_time, phrase) in matches:
        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        count = phrase_counts[phrase]
        # If phrase appears more than once, add a number e.g. walk2.mp4
        clip_output = f"{phrase.replace(' ', '_')}.mp4" if count == 1 else f"{phrase.replace(' ', '_')}{count}.mp4"
        tracker.start_stage("Creating clip")
        print(f"Trigger '{phrase}' detected at {detected_time:.2f}s — saving to {clip_output}")
        create_clip(video_path, detected_time, clip_output)
        tracker.finish_stage()

    # Deletes the original video and audio files
    delete_file(video_path)
    delete_file(audio_path)

    tracker.finish_all()
    print(f"{len(matches)} clip(s) created.")


if __name__ == "__main__":
    main()