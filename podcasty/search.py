"""
A module to interface with spotify & other content providers and obtain episode IDs or URLs 
when only search keywords are available to the user.
"""

import os
from requests import get
from typing import List, Dict
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from youtube_dl import YoutubeDL

SCOPE = "user-library-read"
YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
load_dotenv(".env")


class WebSearch(object):
    """
    Main search wrapper to perform searches on content providers and store results.
    `queries`: A List of strings containing search queries ex.: "Joe Rogan #1571 Emily Harrington"
    `provider`: Either 'YOUTUBE' or 'SPOTIFY' to define the content provider to use for the search.
    `limit`: How many results are returned per query, by default returns only the top 1 result.
    `searchtype`: Flag needed for spotify, by default will look for matching podcast episodes.
    """

    def __init__(
        self,
        queries: List[str],
        provider: str = "SPOTIFY",
        scope: str = SCOPE,
        limit: int = 1,
        searchtype: str = "episode",
        ydl_options: str = YDL_OPTIONS,
    ) -> None:
        super().__init__()
        self.queries = queries
        self.provider = provider
        self.scope = scope
        self.limit = limit
        self.searchtype = searchtype
        self.ydl_options = ydl_options
        self.spotify = (
            None
            if self.provider == "YOUTUBE"
            else spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        )

    def search(self):
        """
        Wrapper to look up results based on the parameters defined upon instantiation of the class.
        Extends the results list and then returns it.
        """
        if self.provider == "SPOTIFY":
            responses = [
                self.spotify.search(q=query, limit=self.limit, type=self.searchtype)
                for query in self.queries
            ]
            results = self.process_responses(responses)
            return results
        elif self.provider == "YOUTUBE":
            responses = [self.youtube_search(query) for query in self.queries]
            results = self.process_responses(responses)
        return results

    def youtube_search(self, query: str) -> Dict:
        """
        Passes `query` to YoutubeDL and return the raw output.
        """
        with YoutubeDL(self.ydl_options) as ydl:
            try:
                get(query)
            except:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)[
                    "entries"
                ][0]
            else:
                result = ydl.extract_info(query, download=False)
        return result

    def process_responses(self, responses: List[Dict]) -> List[Dict]:
        """
        Preprocess raw responses returned by youtube and spotify.
        """
        if self.provider == "YOUTUBE":
            output = [
                {
                    "id": res["id"],
                    "title": res["title"],
                    "description": res["description"],
                    "duration": res["duration"],
                    "url": res["webpage_url"],
                }
                for res in responses
            ]
        elif self.provider == "SPOTIFY" and self.searchtype == "episode":
            output = [
                {
                    "id": res["episodes"]["items"][0]["id"],
                    "title": res["episodes"]["items"][0]["name"],
                    "description": res["episodes"]["items"][0]["description"],
                    "duration": res["episodes"]["items"][0]["duration_ms"]
                    / 1000
                    / 60,  # ms to sec to minutes
                    "url": res["episodes"]["items"][0]["external_urls"]["spotify"],
                }
                for res in responses
            ]
        return output
