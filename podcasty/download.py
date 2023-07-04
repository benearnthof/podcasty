"""
Module to download podcasts as audio files.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, List, Optional
from tqdm import tqdm

from youtube_dl import YoutubeDL

from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.metadata import EpisodeId


load_dotenv(".env")

SPOTIFY_USER = os.environ.get("SPOTIFY_USER", "user")
SPOTIFY_PASSWORD = os.environ.get("SPOTIFY_PASSWORD", "pass")
CREDENTIALS = {"user": SPOTIFY_USER, "password": SPOTIFY_PASSWORD}


class Downloader(object):
    def __init__(
        self,
        urls: List[str],
        filenames: List[str],
        credentials=CREDENTIALS,
        extension="wav",
    ) -> None:
        super().__init__()
        self.extension = extension
        self.file_names = self.make_filenames(filenames)
        self.file_location = Path(gettempdir())
        self.sources = self.infer_sources(urls)
        self.urls = urls
        self.session = (
            (
                Session.Builder()
                .user_pass(credentials["user"], credentials["password"])
                .create()
            )
            if "SPOTIFY" in self.sources
            else None
        )

    def make_filenames(self, filenames: List[str]) -> List[str]:
        """
        Quick wrapper to add extensions to a list of filenames obtained by the Spotify API.
        """
        # todo: replace this as we pass in a list of filenames
        filenames = [f"{filename+'.'+self.extension}" for filename in filenames]
        return filenames

    @staticmethod
    def infer_sources(urls: List[str]) -> List[str]:
        """
        Infer source of download from urls. Currently only YouTube and Spotify are supported.
        """

        def infer(url: str) -> str:
            if "youtube" in url.split("."):
                return "YOUTUBE"
            elif "spotify" in url.split("."):
                return "SPOTIFY"
            else:
                print(url)
                raise NotImplementedError(f"Source for {url} not yet implemented.")

        return [infer(url) for url in urls]

    def download(self) -> List[Dict]:
        """
        Loop over urls, download the content to a temporary location and return a List of Dictionaries
        containing all relevant metadata.
        """
        out = []
        for url, source, filename in tqdm(
            zip(self.urls, self.sources, self.file_names), total=len(self.urls)
        ):
            if source == "YOUTUBE":
                out.append(self.get_youtube(url, self.extension))
            elif source == "SPOTIFY":
                out.append(self.get_spotify(url, filename))
        return out

    @staticmethod
    def get_youtube(url: str, extension: str, filename=Optional[str]) -> Dict:
        """
        Process a single YouTube url wiht YoutubeDL.
        https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script
        Output is saved to temporary directory and all relevant metadata is returned as a Dict.
        """
        # TODO: should be able to digest both 'id' and 'url'
        video_info = YoutubeDL().extract_info(url=url, download=False)
        filename = f"{video_info['title']+'.'+extension}"
        options = {
            "format": "bestaudio/best",
            "keepvideo": False,
            "outtmpl": str(Path(gettempdir(), filename)),
        }
        with YoutubeDL(options) as ydl:
            ydl.download([video_info["webpage_url"]])
        return {"audio": Path(gettempdir(), filename)}

    def get_spotify(self, url: str, filename: str) -> Dict:
        """
        Process a single Spotify url with https://github.com/librespot-org/librespot.
        Obtains the raw audio bytestream from the source
        which is saved to a .wav file in a temporary location.
        Returns all relevant metadata as a Dict.
        """
        access_token = self.session.tokens().get("playlist-read")
        stream_type = "track" if "track" in url.split("/") else "episode"
        # TODO: should be able to digest both 'id' and 'url'
        id = url.split("/")[-1].split("?")[0]
        if stream_type == "track":
            stream_id = TrackId.from_uri(f"spotify:track:{id}")
        elif stream_type == "episode":
            stream_id = EpisodeId.from_uri(f"spotify:episode:{id}")
        try:
            stream = self.session.content_feeder().load(
                stream_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None
            )
            with open(Path(gettempdir(), filename), "wb") as file:
                # TODO: add progress bar since downloads for long episodes are slow
                bytestream = stream.input_stream.stream().read(-1)
                file.write(bytestream)
                file.close()
        except:
            print(f"\nUnable to download: {filename}")  # TODO: log this
            return {"audio": Path(gettempdir(), filename)}
        # https://github.com/ozora-ogino/spotify_dlx/blob/main/spotify_dlx/utils.py
        # https://github.com/kokarare1212/librespot-python/issues/101

        # session.close()  # added this to test if this fixes problems with parallel downloads
        return {"audio": Path(gettempdir(), filename)}


def parallel_dl_wrapper(url: str, name: str):
    """Simple Wrapper to interface with joblib::Parallel"""
    dl = Downloader([url], [name])
    metadata = dl.download()
    return metadata
