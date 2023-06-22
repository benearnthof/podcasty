# podcasty: A CLI to download, transcribe, translate, and summarize podcasts written in Python

Currently can only download and transcribe from YouTube and Spotify (work in progress).  
Add to issues for feature requests. 

General Use:  
1. Create a `.env` file with your Spotify Device Credentials like so:
```
# Spotify Variables
SPOTIFY_USER=YOUR_DEVICE_ID
SPOTIFY_PASSWORD=YOUR_DEVICE_PASSWORD
```

2. Get a list of episodes you would like to download and instantiate the Downloader
```
youtube_url = "https://www.youtube.com/watch?v=qipKKBmY_LQ"
spotify_url = "https://open.spotify.com/episode/1P6wgzkVhfUBt0T0qCBhqv?si=a18c66cae3cb4e14"

urls = [youtube_url, spotify_url]

from podcasty.download import Downloader
bulk_downloader = Downloader(urls, filename="testname")
bulk_metadata = bulk_downloader.download()
```
3. The episode audio data can now be found in the form of .wav files in the locations saved to the metadata