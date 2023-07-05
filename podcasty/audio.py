"""
Utilities to convert different file formats to numpy arrays that can be fed to the whisper model. 
Useful in cases where ffmpeg can not be run on the GPU device (server, cluster, etc.), so 
the conversion to numpy arrays can be done as a preprocessing step on a local machine.
"""

import os
from functools import lru_cache
from subprocess import CalledProcessError, run
from typing import Optional, Union, List
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np

# default values for whisper
SAMPLE_RATE = 16000

files = os.listdir()

mp3 = [file for file in files if file.endswith("mp3")]
mp4 = [file for file in files if file.endswith("mp4")]

files = mp4


def convert_mp4(files: List[str]):
    """
    Converts Videos to mp3 for downstream audio processing.
    files: List of file names in the working directory that will be converted.
    """
    names = [file.removesuffix(".mp4") for file in files]
    commands = []
    for file, name in tqdm(zip(files, names), total=len(files)):
        commands.append(
            ["ffmpeg", "-i", f"{file}", "-b:a", "192K", "-vn", f"{name}.mp3"]
        )
    try:
        out = Parallel(n_jobs=4, prefer="processes", timeout=999999)(
            delayed(run)(cmd, capture_output=True, check=True) for cmd in tqdm(commands)
        )
        # run(cmd, capture_output=True, check=True).stdout
    except CalledProcessError as e:
        # TODO: Log this and proceed with the next file
        raise RuntimeError(f"Failed to load video: {e.stderr.decode()}") from e


# convert_mp4(files=mp4)

# res = Parallel(n_jobs=2, prefer="processes", timeout=999999)(
#     delayed(run)(cmd, capture_output=True, check=True).stdout
# )


def convert_mp3(files: List[str]):
    """
    Utility for converting mp3 to wav.
    Will result in loss of quality and inflation of file size, not recommended.
    files: List of file names in the working directory that will be converted.
    """
    names = [file.removesuffix(".mp3") for file in files]
    commands = []
    for file, name in tqdm(zip(files, names), total=len(files)):
        commands.append(["ffmpeg", "-i", f"{file}", "-ar", "16000", f"{name}.wav"])
        # not recommended will result in massive quality loss compared to mp3
    try:
        out = Parallel(n_jobs=4, prefer="processes", timeout=999999)(
            delayed(run)(cmd, capture_output=True, check=True) for cmd in tqdm(commands)
        )
        # run(cmd, capture_output=True, check=True).stdout
    except CalledProcessError as e:
        # TODO: Log this and proceed with the next file
        raise RuntimeError(f"Failed to load video: {e.stderr.decode()}") from e


# convert_mp3(files=mp3)


def convert_numpy(files: List[str], sr: int = SAMPLE_RATE):
    """
    Utility to convert audio to numpy so downstream processing does not depend on ffmpeg.
    """
    names = [file[:-3] for file in files]
    commands = []
    for file, name in tqdm(zip(files, names), total=len(files)):
        commands.append(
            [
                "ffmpeg",
                "-nostdin",
                "-threads",
                "0",
                "-i",
                file,
                "-f",
                "s16le",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(sr),
                "-",
            ]
        )
