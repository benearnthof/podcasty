from podcasty.search import WebSearch
from typing import List

queries = ["Joe Rogan #1571 Emily Harrington"]

ws = WebSearch(queries=queries)

res = ws.search()

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

queries = [f"Joe Rogan {episode[0]} {episode[1].split(',')[0]}" for episode in episodes]
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
