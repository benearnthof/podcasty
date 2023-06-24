from podcasty.search import WebSearch

queries = ["Joe Rogan #1571 Emily Harrington"]

ws = WebSearch(queries=queries)

res = ws.search()
