"""
Module to transcribe an mp3 to a text file.
"""

from whisper import load_model
from pathlib import Path
from typing import Dict
from tempfile import gettempdir

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
    doc = file["mp3"]
    assert doc.exists()
    # if transcription throws winerror make sure ffmpeg is installedd and added to PATH
    transcription = model.transcribe(str(doc))
    # output transcript as text file to same temporary directory
    out_path = Path(doc.parent / Path(str(doc.stem) + ".txt"))
    with open(out_path, "w") as text_file:
        # TODO: Should tokens and probabilities be preserved for downstream tasks?
        text_file.write(transcription["text"])
    file["txt"] = out_path
    return file
