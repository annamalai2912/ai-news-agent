# debug.py
import feedparser
from news_sources import from_rss, FEEDS
from googlenewsdecoder import gnewsdecoder

for name, url in FEEDS.items():
    d = feedparser.parse(url)
    print(f"{name:18} entries={len(d.entries):3}  http={d.get('status')}")

gn = [x for x in from_rss() if x["source"].startswith("News:")]
print("\nGoogle News items from last 24h:", len(gn))
for x in gn[:3]:
    print("\nTRYING:", x["title"][:70])
    try:
        print(gnewsdecoder(x["url"], interval=1))
    except Exception as e:
        print("EXCEPTION:", repr(e))