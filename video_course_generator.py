import os
import subprocess
from openai import OpenAI
from fastapi import APIRouter, UploadFile, File, HTTPException

import os

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

# In your endpoint, use:
# client = get_openai_client()


router = APIRouter()



def extract_audio_from_video(video_path: str, audio_path: str):
    """
    Use ffmpeg to extract audio from the video file and save as WAV.
    """
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",           # no video
        "-acodec", "pcm_s16le",  # PCM 16-bit little-endian WAV codec
        "-ar", "16000",  # 16k sampling rate (recommended for Whisper)
        "-ac", "1",      # mono audio channel
        audio_path,
        "-y"             # overwrite output file if exists
    ]
    subprocess.run(command, check=True)

@router.post("/transcribe-video")
async def transcribe_video(video_file: UploadFile = File(...)):
    # Validate file type (optional)
    if not video_file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Paths
    upload_folder = "./uploads"
    os.makedirs(upload_folder, exist_ok=True)
    video_path = os.path.join(upload_folder, video_file.filename)
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"

    # Save uploaded video
    with open(video_path, "wb") as buffer:
        buffer.write(await video_file.read())

    # Extract audio from video
    try:
        extract_audio_from_video(video_path, audio_path)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to extract audio from video")

    # CREATE CLIENT HERE (not globally)
    client = get_openai_client()  # ADD THIS LINE

    # Read audio file for transcription
    with open(audio_path, "rb") as audio_file:
        transcript_response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )

    # Return transcription text
    return {
        "transcription": transcript_response.text,
        "video_filename": video_file.filename,
        "audio_extracted": os.path.basename(audio_path)
    }

