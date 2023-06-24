"""
Tests for podcasty.download.py
"""

TEST_URL = "https://www.youtube.com/watch?v=qipKKBmY_LQ"

yt = "https://www.youtube.com/watch?v=qipKKBmY_LQ"
sp = "https://open.spotify.com/episode/1P6wgzkVhfUBt0T0qCBhqv?si=a18c66cae3cb4e14"

urls = [yt, sp]

from podcasty.download import Downloader

fname = "1571 Emily Harrington"
downloader = Downloader(urls=[sp], filename=fname)

assert downloader.extension == "wav"
assert downloader.file_location.exists()
assert len(downloader.file_names) == 1
assert downloader.file_names[0] == fname + "_0." + downloader.extension
assert downloader.sources == ["SPOTIFY"]
assert downloader.urls == [
    "https://open.spotify.com/episode/1P6wgzkVhfUBt0T0qCBhqv?si=a18c66cae3cb4e14"
]
assert downloader.credentials is not None

metadata = downloader.download()

assert metadata[0]["audio"].exists()

bulk_downloader = Downloader(urls, filename="testname")
assert bulk_downloader.extension == "wav"
assert bulk_downloader.file_location.exists()
assert len(bulk_downloader.file_names) == 2
assert bulk_downloader.sources == ["YOUTUBE", "SPOTIFY"]
assert bulk_downloader.urls
assert bulk_downloader.credentials

bulk_metadata = bulk_downloader.download()
