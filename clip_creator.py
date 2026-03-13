from moviepy.editor import VideoFileClip


def create_clip(video_path, start_time, output_path, clip_duration=20):
    """
    Creates a clip that ends right when the voiceline is said.

    Args:
        video_path (str): Path to the original video file.
        start_time (float): The timestamp (in seconds) where the voiceline is detected.
        output_path (str): Path where the clip will be saved.
        clip_duration (int, optional): Duration of the clip in seconds. Default is 30.
    """
    try:
        # Clip ends right as the voiceline is said, starts clip_duration seconds before
        clip_end = start_time
        clip_start = max(0, clip_end - clip_duration)

        # Load the original video
        video = VideoFileClip(video_path)

        # Create the subclip
        subclip = video.subclip(clip_start, clip_end)

        # Write the clip to a file
        subclip.write_videofile(output_path, codec="libx264")
        print(f"Clip created and saved to {output_path}")
    except Exception as e:
        print(f"An error occurred while creating the clip: {e}")


if __name__ == "__main__":
    video_path = "video.mp4"
    start_time = 60  # example timestamp in seconds
    output_path = "voiceline1.mp4"
    create_clip(video_path, start_time, output_path)