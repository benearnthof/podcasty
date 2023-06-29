from podcasty.search import WebSearch
from typing import List

queries = ["Joe Rogan #1571 Emily Harrington"]

ws = WebSearch(queries=queries)

default = ws.search()

with open("jrelist.txt", encoding="utf-8") as file:
    lines = [line.rstrip() for line in file]

line = lines[0]

splits = [line.split("\t") for line in lines]

numbers = [entry[0] for entry in splits]

# TODO: refactor this mess
episodes = [entry for entry in splits if entry[0].startswith("#")]
other = [entry for entry in splits if not entry[0].startswith("#")]
mmashow = [entry for entry in other if entry[0].startswith("MMA")]
other = [entry for entry in other if not entry[0].startswith("MMA")]
fightcomp = [entry for entry in other if entry[0].startswith("Fight")]
other = [entry for entry in other if not entry[0].startswith("Fight")]
ufc = [entry for entry in other if entry[0].startswith("UFC")]
extra = [entry for entry in other if not entry[0].startswith("UFC")]
# 18 episodes are left


numbers = [int(entry[0][1:]) for entry in episodes]

s = sorted(numbers)

# 1712 is in list twice => Bert Kreischer Episode that was split into two parts
# check encoding
for i, entry in enumerate(episodes[:500]):
    print(i, entry)

# check if all guest names are present
for i, episode in enumerate(episodes):
    if not episode[1]:
        print(i)

# only 1992 and 1994 have no guest => Joe Rogan himself
# every query has the following structure:
# "Joe Rogan `number` `name`"

queries = [f"{episode[0]} - {episode[1].split(',')[0]}" for episode in episodes]
queries_extra = [
    f"Joe Rogan {episode[0]} {episode[1].split(',')[0]}" for episode in extra
]

# lets see what the results look like
# there should be over 100 episodes missing

ws = WebSearch(queries=queries)

res = ws.search()

titles = [entry["title"] for entry in res]
# titles have ot start with #
mismatches = [entry for entry in titles if not entry.startswith("#")]
not_mismatched = [entry for entry in titles if entry.startswith("#")]

# title beginnings should match their respective episode numbers
# 113 episodes are missing from spotify
# 3 episodes have been shortened

import pickle

with open("jre_results.pickle", "wb") as handle:
    pickle.dump(res, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("jre_results.pickle", "rb") as handle:
    results = pickle.load(handle)

all([len(entry) >= 10 for entry in queries])
matches = [
    result
    for result, query in zip(results, queries)
    if result["title"][0:10] == query[0:10]
]
len(matches)  # got 1567 good results
# checking which queries failed
mismatches = [
    (result, query)
    for result, query in zip(results, queries)
    if result["title"][0:10] != query[0:10]
]

mismatched_queries = [entry[1] for entry in mismatches]

# trying to run the mismatched queries again without "Joe Rogan" in front and with the added hyphen

ws = WebSearch(queries=mismatched_queries)
results2 = ws.search()

with open("jre_results2.pickle", "wb") as handle:
    pickle.dump(results2, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("jre_results2.pickle", "rb") as handle:
    results2 = pickle.load(handle)

matches2 = [
    result
    for result, query in zip(results2, mismatched_queries)
    if result["title"][0:10] == query[0:10]
]

remaining_mismatches = [
    (result, query)
    for result, query in zip(results2, mismatched_queries)
    if result["title"][0:10] != query[0:10]
]
len(remaining_mismatches)
# 390 remaining, 113 of which are episodes that have been removed from spotify
mismatched_queries2 = [entry[1] for entry in remaining_mismatches]

with open("mis_queries2.pickle", "wb") as handle:
    pickle.dump(mismatched_queries2, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("mis_queries2.pickle", "rb") as handle:
    mismatched_queries2 = pickle.load(handle)

# lets assume the target episode is not in the top 1 spot, but the top 5 spots
import os
from requests import get
from typing import List, Dict
from dotenv import load_dotenv
from tqdm import tqdm

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
load_dotenv(".env")

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


responses_3 = [
    spotify.search(q=query, limit=5, type="episode")
    for query in tqdm(mismatched_queries2)
]

# default = spotify.search(q="Joe Rogan #1571 Emily Harrington", limit=1, type="episode")
# len(default["episodes"]["items"])

with open("jre_results3.pickle", "wb") as handle:
    pickle.dump(responses_3, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("jre_results3.pickle", "rb") as handle:
    responses_3 = pickle.load(handle)

responses_3[0].keys()
# unwrap the first dict since it has only one key
eps = [entry["episodes"] for entry in responses_3]

ep = eps[0]

lengths = [len(ep) for ep in eps]

items = ep["items"]
item = items[0]

from difflib import SequenceMatcher as SM
import numpy as np


def get_best_episode_match(query: str, items: List[Dict]) -> Dict:
    """
    Find out which item in the list of responses with limit > 1 contains the title that matches the
    query most closely.
    """
    titles = [item["name"] for item in items]
    matches = [SM(None, query, title).ratio() for title in titles]
    closest_match = items[np.argmax(matches)]
    closest_match["score"] = matches[np.argmax(matches)]
    return closest_match


closest_matches = [
    get_best_episode_match(q, ep["items"]) for q, ep in zip(mismatched_queries2, eps)
]

scores = [entry["score"] for entry in closest_matches]

pairs = [
    (score, match["name"], query)
    for score, match, query in zip(scores, closest_matches, mismatched_queries2)
]

# another 170 episodes found with high accuracy
jre_results4 = [entry for entry in closest_matches if entry["score"] == 1.0]

with open("jre_results4.pickle", "wb") as handle:
    pickle.dump(jre_results4, handle, protocol=pickle.HIGHEST_PROTOCOL)

fuzzy_mismatches = [entry for entry in closest_matches if entry["score"] < 1.0]
fuzzy_queries = [
    query
    for entry, query in zip(closest_matches, mismatched_queries2)
    if entry["score"] < 1.0
]
fuzzy_scores = [entry["score"] for entry in fuzzy_mismatches]
fuzzy_pairs = [
    (score, match["name"], query)
    for score, match, query in zip(fuzzy_scores, fuzzy_mismatches, fuzzy_queries)
]

# there are still some matches in here with scores < 1 because of missing commas
jre_results5 = [
    entry
    for entry, query in zip(fuzzy_mismatches, fuzzy_queries)
    if entry["name"].split(" ")[0] == query.split(" ")[0]
]

with open("jre_results5.pickle", "wb") as handle:
    pickle.dump(jre_results5, handle, protocol=pickle.HIGHEST_PROTOCOL)

final_mismatches = [
    entry
    for entry, query in zip(fuzzy_mismatches, fuzzy_queries)
    if not entry["name"].split(" ")[0] == query.split(" ")[0]
]
final_queries = [
    query
    for entry, query in zip(fuzzy_mismatches, fuzzy_queries)
    if not entry["name"].split(" ")[0] == query.split(" ")[0]
]

# 189 episodes remain, of which 113 are not on spotify
# This means this approach fails only for 76 episodes
final_pairs = [
    (match["name"], query) for match, query in zip(final_mismatches, final_queries)
]

with open("jremissing.txt", encoding="utf-8") as file:
    jremissing = [line.rstrip() for line in file]

missing = [
    f"{entry.split(' ', 1)[0]} - {entry.split(' ', 1)[1]}" for entry in jremissing
]

nonmissing_episodes = [query for query in final_queries if not query in missing]
missing_episodes = [query for query in final_queries if query in missing]


import os
from requests import get
from typing import List, Dict
from dotenv import load_dotenv
from tqdm import tqdm

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
load_dotenv(".env")

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


test = spotify.show_episodes(show_id="4rOoJ6Egrf8K2IrywzwOMk", limit=1)

jre_episodes = []
for index in tqdm(range(2000, 2163)):
    response = spotify.show_episodes(
        show_id="4rOoJ6Egrf8K2IrywzwOMk", limit=1, offset=index
    )
    jre_episodes.append(response)
    print(response["items"][0]["name"])

uniques = []
unique_items = 0

for item in jre_episodes:
    if item not in uniques:
        uniques.append(item)
        unique_items += 1

with open("JRE_SPOTIFY_COMPLETE.pickle", "wb") as handle:
    pickle.dump(jre_episodes, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open("JRE_SPOTIFY_COMPLETE.pickle", "rb") as handle:
    jre = pickle.load(handle)

jre_uris = [ep["items"][0]["uri"] for ep in jre if ep["items"]]
jre_names = [ep["items"][0]["name"] for ep in jre if ep["items"]]
jre_urls = [ep["items"][0]["external_urls"]["spotify"] for ep in jre if ep["items"]]


with open("jre_uris.txt", "w") as f:
    for line in jre_uris:
        f.write(f"{line}\n")


if __name__ == "__main__":
    import pickle
    import multiprocessing
    from podcasty.download import Downloader, bulk_dl, debug

    with open("JRE_SPOTIFY_COMPLETE.pickle", "rb") as handle:
        jre = pickle.load(handle)
    jre_uris = [ep["items"][0]["uri"] for ep in jre if ep["items"]]
    jre_names = [ep["items"][0]["name"] for ep in jre if ep["items"]]
    jre_urls = [ep["items"][0]["external_urls"]["spotify"] for ep in jre if ep["items"]]
    with multiprocessing.Pool(processes=1) as pool:
        results = pool.starmap(bulk_dl, zip(jre_urls, jre_names))
    print(results)

import itertools

test = [itertools.starmap(jre_urls, jre_names)]
# doesnt work with windows 10

from joblib import Parallel, delayed

urls = jre_urls[113:]
names = jre_names[113:]

res = Parallel(n_jobs=8)(delayed(bulk_dl)(url, name) for url, name in zip(urls, names))

# 56 mbps


def bulk_dl(url, name):
    dl = Downloader(urls=[url], filename=name)
    metadata = dl.download()
    return metadata


for url, name in tqdm(zip(urls, names), total=len(urls)):
    _ = bulk_dl(url, name)
