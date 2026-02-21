from moviepy import VideoFileClip

def extract_audio(video_path, output_audio_path):
    """
    Extracts audio from a video file and saves it as a WAV file.

    Args:
        video_path (str): Path to the input video file.
        output_audio_path (str): Path where the extracted audio will be saved.
    """
    try:
        # Load the video file
        video_clip = VideoFileClip(video_path)
        # Write the audio to a WAV file
        video_clip.audio.write_audiofile(output_audio_path)
        print(f"Audio extracted and saved to {output_audio_path}")
    except Exception as e:
        print(f"An error occurred during audio extraction: {e}")

# Example usage:
if __name__ == "__chopped_main__":
    video_path = "your_video.mp4"
    output_audio_path = "extracted_audio.wav"
    extract_audio(video_path, output_audio_path)