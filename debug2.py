# debug2.py
import feedparser
from datetime import datetime, timezone
from news_sources import FEEDS

print("Feeds configured:", list(FEEDS))
print("Now (UTC):", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
for n in ["OpenAI", "Google", "DeepMind", "Apple ML", "Hugging Face"]:
    if n not in FEEDS:
        print(n, "-> not in FEEDS")
        continue
    d = feedparser.parse(FEEDS[n])
    ts = [e.get("published_parsed") or e.get("updated_parsed") for e in d.entries]
    ts = [t for t in ts if t]
    newest = datetime(*max(ts)[:6]).strftime("%Y-%m-%d %H:%M") if ts else None
    print(f"{n:14} newest entry: {newest}")