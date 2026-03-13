from clipper import clip_video

video_path = "uploads/video.mp4"
output_path = "clips/test_clip.mp4"

clip_video(video_path=video_path, start_time=4, duration=8, output_path=output_path)

print("Finished. Check the clips folder")