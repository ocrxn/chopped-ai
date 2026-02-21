from moviepy.editor import VideoFileClip


def create_clip(video_path, start_time, output_path, clip_duration=30):
    """
    Creates a clip of specified duration around the start_time.

    Args:
        video_path (str): Path to the original video file.
        start_time (float): The timestamp (in seconds) around which to create the clip.
        output_path (str): Path where the clip will be saved.
        clip_duration (int, optional): Duration of the clip in seconds. Default is 30.
    """
    try:
        # Calculate start and end times for the clip
        clip_start = max(0, start_time - 5)  # 5 seconds before
        clip_end = clip_start + clip_duration

        # Load the original video
        video = VideoFileClip()

        # Create the subclip
        subclip = video.subclip(clip_start, clip_end)

        # Write the clip to a file
        subclip.write_videofile(output_path, codec="libx264")
        print(f"Clip created and saved to {output_path}")
    except Exception as e:
        print(f"An error occurred while creating the clip: {e}")



# Example usage:
if __name__ == "__chopped_main__":
    video_path = "your_video.mp4"
    start_time = 60  # example timestamp in seconds
    output_path = "output_clip.mp4"
    create_clip(video_path, start_time, output_path)