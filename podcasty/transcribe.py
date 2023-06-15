"""
Module to transcribe an mp3 to a text file.
"""

from whisper import load_model
from pathlib import Path
from typing import Dict

# TODO: remove this
from podcasty.download import get_mp3

URL = "https://www.youtube.com/watch?v=qipKKBmY_LQ"
file = get_mp3(URL)

# TODO: Cache Models somewhere to speed up initialization
MODEL = load_model("medium")


def transcribe(file: Dict, model=MODEL) -> list:
    """
    Use Whisper to transcribe the mp3 given in `file["destination"]`.
    file: Dictionary that is returned by `podcasty.get_mp3`
    """
    doc = file["destination"]
    assert doc.exists()
    # TODO: [WinError 2] The system cannot find the file specified
    transcription = model.transcribe(str(doc))
    pass
