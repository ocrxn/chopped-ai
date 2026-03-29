import os
import sys
import subprocess
import time
from datetime import datetime
import shutil


class FileHandler():
    def __init__(self):
        pass

    def detect_hardware_encoder(self):
        try:
            result = subprocess.run(["ffmpeg", "-encoders"], 
                                    capture_output=True, text=True)
            encoders = result.stdout

            if "h264_videotoolbox" in encoders:
                return "h264_videotoolbox"
            if "h264_nvenc" in encoders:
                return "h264_nvenc"
            if "h264_qsv" in encoders:
                return "h264_qsv"
            
            return None
        except Exception:
            return None


    def compress_video(self, kwargs):
        filename = kwargs.get("vid_filename")
        video_path = kwargs.get("video_path")
        vid_ext = kwargs.get("vid_ext")
        output_dir = kwargs.get("output_dir")

        if not filename or not video_path:
            return
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        encoding_mode = kwargs.get("encoding")
        hw_encoder = self.detect_hardware_encoder()


        cpu_codecs = {
            "mp4": "libx264",
            "mkv": "libx265",
            "webm": "libvpx-vp9",
            "mov": "libx264"
        }

        hw_codecs = {
            "mp4": hw_encoder,
            "mkv": hw_encoder,
            "webm": "libvpx-vp9",
            "mov": hw_encoder
        }

        #If available and enabled, swap to hardware encoding for accelerated processing
        if encoding_mode == "gpu" and hw_encoder:
            video_codec = hw_codecs.get(vid_ext, hw_encoder)
        else:
            video_codec = cpu_codecs.get(vid_ext, "libx264")
                        
        #Initial ffmpeg args
        cmd = ["ffmpeg","-y", "-i", video_path]
        cmd += ["-vf", "scale=1280:-2:force_original_aspect_ratio=decrease", "-c:v", video_codec]

        if video_codec == "libvpx-vp9":
            cmd += ["-crf", "35", 
                        "-b:v", "0", 
                        "-deadline", "realtime", 
                        "-cpu-used", "4"]        
        elif video_codec in ["libx264", "libx265"]:
            cmd += ["-crf", "28", "-preset", "faster"]
        else:
            cmd += ["-b:v", "4M", "-maxrate", "6M", "-bufsize", "12M"]
    
        audio_codec = "libopus" if vid_ext == "webm" else "aac"
        cmd += ["-c:a", audio_codec, "-b:a", "128k"]
        cmd.append(output_path)

        try:
            #Run the ffmpeg command and time the results
            original_size = os.path.getsize(video_path)
            start_time = time.perf_counter()

            if os.path.exists(output_path):
                os.remove(output_path)
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            # Get compressed file size
            compressed_size = 0
            ratio = 0.0
            status = "success"

            if os.path.exists(output_path):
                compressed_size = os.path.getsize(output_path)
                ratio = original_size / compressed_size
            
            #Revert to original video if new video is larger
            if compressed_size > original_size:
                os.remove(output_path)
                shutil.copy(video_path,output_path)
                compressed_size = original_size
                status = "Compression Failed: Kept Original"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_text = (
            f"[{timestamp}] File: {filename}\n"
            f"Encoding type: {encoding_mode}\n"
            f"Hardware Encoder: {hw_encoder}\n"
            f"Video Codec: {video_codec}\n"
            f"Original size: {original_size / 1024:.2f} KB\n"
            f"Compressed size: {compressed_size / 1024:.2f} KB\n"
            f"Compression ratio: {ratio:.2f}x smaller\n"
            f"Time taken: {elapsed:.2f} seconds or ~{(elapsed/60):.1f} minutes\n"
            f"Status: {status}\n"
            "----------------------------------------\n"
        )
            log_file_path = os.path.join(output_dir, "compression_log.txt")
            with open(log_file_path, "a") as f:
                f.write(log_text)
            return {"status": "success", "cmpr_size": compressed_size}
        
        except subprocess.CalledProcessError as e:
            print(f"--- FFMPEG LOG START ---")
            print(e.stderr) 
            print(f"--- FFMPEG LOG END ---")
            log_file_path = os.path.join(output_dir, "compression_log.txt")
            with open(log_file_path, "a") as f:
                f.write(f"[{datetime.now()}] ERROR on {filename}: {e.stderr}\n")
            return {"status": "error", "message": e}
