import os
from serpapi import GoogleSearch

API_KEY = os.getenv("SERPAPI_API_KEY")

search = GoogleSearch({"q": "咖啡 芭提雅", "api_key": API_KEY})
data = search.get_dict()

for r in (data.get("organic_results") or [])[:3]:
    print("·", r.get("title"), "→", r.get("link"))

print("任务完成 ✅")
