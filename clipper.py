#cuts a highlight clip from a video
#uses FFmpeg when given a video path and timestamps

from __future__ import annotations

import subprocess #lets Python run other programs on computer (FFmpeg)
from pathlib import Path #necessary for working with folders

class FFmpegError(RuntimeError):
    pass
#create error for if FFmpeg fails

def cut_clip(
        video_path:str,
        start_time: float,
        duration: float,
        output_path: str,
) -> Path:
    
    # create a Path object and ensure folder exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    command = [
            "ffmpeg",
            "-y",                   #overwrite output if it exists already
            "-ss", str(start_time), #seek to the start time (seconds)
            "-i", video_path,       #input video file
            "-t", str(duration),     #how long clip should be
            "-c:v", "libx264",      #encode video using H.264
            "-c:a", "aac",          #encode audio using AAC
            output_path,
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise FFmpegError("FFmpeg failed to create the clip.") from e

    return output_file