import time
from audio_extractor import extract_audio
from speech_recognition import transcribe_audio
from clip_creator import create_clip

# Your video and voiceline
video_path = "your_video.mp4"
audio_path = "extracted_audio.wav"
output_clip_path = "detected_voiceline_clip.mp4"

# List of phrases to trigger the clip
trigger_phrases = ["single", "error", "strikeout", "flyout", "walk", "double", "triple", "groundout",  ]

def main():
    # Step 1: Extract audio from video
    print("Extracting audio from video...")
    extract_audio(video_path, audio_path)

    # Step 2: Transcribe audio
    print("Transcribing audio...")
    transcript = transcribe_audio(audio_path)
    if transcript:
        print("Transcript received.")
        print(transcript)
    else:
        print("No transcription available.")
        return

    # Step 3: Check for trigger phrases
    transcript_lower = transcript.lower()
    if any(phrase in transcript_lower for phrase in trigger_phrases):
        print("Trigger phrase detected!")

        # WARNING: Without timestamp info, assume start or add custom detection
        # For demonstration, assume timestamp at 10 seconds
        detected_time = 10  # You should replace this with real timestamp detection
        print(f"Creating clip around {detected_time} seconds...")

        # Step 4: Create 30-second clip around the detected time
        create_clip(video_path, detected_time, output_clip_path)
    else:
        print("No trigger phrases found in transcript.")

if __name__ == "__main__":
    main()