"""
Module to download podcasts as audio files.
"""

from pathlib import Path
from tempfile import gettempdir
from typing import Dict
from youtube_dl import YoutubeDL


def get_mp3(url: str) -> Dict:
    """
    Use `url` to obtain mp3 from youtube.
    """
    video_info = YoutubeDL().extract_info(url=url, download=False)
    filename = f"{video_info['title']}.mp3"
    options = {
        "format": "bestaudio/best",
        "keepvideo": False,
        "outtmpl": str(Path(gettempdir(), filename)),
    }
    with YoutubeDL(options) as ydl:
        ydl.download([video_info["webpage_url"]])
    return {"destination": Path(gettempdir(), filename)}
