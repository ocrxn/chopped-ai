import os
from audio_extractor import extract_audio
from speech_recognition import transcribe_audio_with_whisper
from clip_creator import create_clip
from video_upload import convert_to_standard
from timer import ProgressTracker

# List of phrases to trigger the clip
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


def main():
    tracker = ProgressTracker()

    # Step 1: Find and convert video to video.mp4
    print("Searching for video file...")
    if not convert_to_standard():
        return

    video_path = "video.mp4"
    audio_path = "audio.wav"
    output_clip_path = "detected_voiceline_clip.mp4"

    # Step 2: Extract audio
    tracker.start_stage("Extracting audio")
    extract_audio(video_path, audio_path)
    tracker.finish_stage()

    # Step 3: Transcribe audio
    tracker.start_stage("Transcribing audio")
    segments = transcribe_audio_with_whisper(audio_path)
    tracker.finish_stage()

    if not segments:
        print("No transcription available.")
        return

    print(f"Transcription complete. {len(segments)} segments found.")

    # Step 4: Search for trigger phrases
    matches = find_trigger_segments(segments, trigger_phrases)
    if not matches:
        print("No trigger phrases found in transcript.")
        tracker.finish_all()
        return

    # Step 5: Create a clip for each trigger
    for i, (detected_time, phrase) in enumerate(matches):
        clip_output = f"voiceline{i + 1}.mp4"
        tracker.start_stage("Creating clip")
        print(f"Trigger '{phrase}' detected at {detected_time:.2f}s — saving to {clip_output}")
        create_clip(video_path, detected_time, clip_output)
        tracker.finish_stage()

    # Step 6: Delete the original video now that we're done with it
    if os.path.exists(video_path):
        os.remove(video_path)
        print(f"Deleted {video_path}")

    tracker.finish_all()
    print(f"{len(matches)} clip(s) created.")


if __name__ == "__main__":
    main()