import requests
import json

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Wa1zX6SawhSkzALxPElcw", "isbns": "0380795272"})
bookData = res.json()['books'][0]
print(json.dumps(bookData, sort_keys = True, indent = 4))