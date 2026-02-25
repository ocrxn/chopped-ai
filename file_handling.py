import os
import sys
import subprocess


class FileHandler():
    def __init__(self):
        pass

    def compress_video(self, kwargs):
        result = subprocess.run(["ls", "-l"], capture_output=True,text=True)
        for key,value in kwargs.items():
            print(f"{key}: {value}")
        return result.stdout

    def compress_audio(self):
        pass