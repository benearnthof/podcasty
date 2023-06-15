"""
Module to transcribe an mp3 to a text file.
"""

from whisper import load_model
from pathlib import Path
from typing import Dict

# TODO: Cache Models somewhere to speed up initialization
MODEL = load_model("medium")


def transcribe(file: Dict, model=MODEL) -> list:
    """
    Use Whisper to transcribe the mp3 given in `file["destination"]`.
    file: Dictionary that is returned by `podcasty.get_mp3`
    """
    pass
