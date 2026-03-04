import whisper


def transcribe_audio_with_whisper(audio_path):
    """
    Transcribes audio using Whisper, returning segments with timestamps.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        list: List of segments with start, end, and text.
    """
    # Load the Whisper model (choose 'tiny', 'base', 'small', 'medium', 'large' based on your hardware)
    model = whisper.load_model("base")  # Change to 'small', 'medium', etc., as needed

    # Transcribe the audio
    result = model.transcribe(audio_path)

    # Get segments with timestamps
    segments = result['segments']
    return segments


# Example usage:
if __name__ == "__main__":
    audio_path = "extracted_audio.wav"
    segments = transcribe_audio_with_whisper(audio_path)
    for segment in segments:
        print(f"{segment['start']:.2f} - {segment['end']:.2f}: {segment['text']}")