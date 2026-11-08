# news_sources.py
import requests, feedparser
from googlenewsdecoder import gnewsdecoder
from datetime import datetime, timezone, timedelta

FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google": "https://blog.google/technology/ai/rss/",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "Microsoft": "https://blogs.microsoft.com/ai/feed/",
    "Apple ML": "https://machinelearning.apple.com/rss.xml",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    # Anthropic and Meta have no reliable official RSS; Google News queries cover them
    "News: Anthropic": "https://news.google.com/rss/search?q=Anthropic+(launch+OR+model+OR+release+OR+research)+when:1d",
    "News: Meta AI": "https://news.google.com/rss/search?q=Meta+AI+(launch+OR+model+OR+Llama+OR+research)+when:1d",
}
FEEDS.pop("Microsoft", None)
FEEDS["News: Microsoft AI"] = "https://news.google.com/rss/search?q=Microsoft+AI+(launch+OR+model+OR+Copilot+OR+research)+when:1d"
FEEDS["News: Apple AI"] = "https://news.google.com/rss/search?q=Apple+Intelligence+(launch+OR+model+OR+research)+when:1d"
HN_QUERIES = ["Anthropic", "Claude", "OpenAI", "Gemini", "Meta AI", "Llama",
              "Apple Intelligence", "LLM"]

def cutoff():
    return datetime.now(timezone.utc) - timedelta(hours=24)

SKIP_DOMAINS = ("fourweekmba.com", "stocktitan.net", "fool.com", "kucoin.com")

def from_rss():
    items, limit = [], cutoff()
    for name, url in FEEDS.items():
        try:
            entries = feedparser.parse(url).entries
        except Exception:
            continue
        recent = []
        for e in entries:
            t = e.get("published_parsed") or e.get("updated_parsed")
            if not t:
                continue
            dt = datetime(*t[:6], tzinfo=timezone.utc)
            if dt >= limit:
                recent.append((dt, e))
        recent.sort(key=lambda x: x[0], reverse=True)
        is_gnews = name.startswith("News:")
        for dt, e in recent[:8]:
            items.append({"source": name, "title": e.title, "url": e.link,
                          "text": "" if is_gnews else e.get("summary", "")[:400]})
    return items

def from_hn():
    items, seen = [], set()
    ts = int(cutoff().timestamp())
    for q in HN_QUERIES:
        try:
            r = requests.get("https://hn.algolia.com/api/v1/search_by_date",
                             params={"query": q, "tags": "story",
                                     "numericFilters": f"created_at_i>{ts},points>30"},
                             timeout=20).json()
        except Exception:
            continue
        for h in r.get("hits", []):
            if h["objectID"] in seen or not h.get("url"):
                continue
            seen.add(h["objectID"])
            items.append({"source": f"HN ({h['points']} pts)", "title": h["title"],
                          "url": h["url"], "text": ""})
    return items

def resolve(url):
    if "news.google.com" not in url:
        return url
    try:
        r = gnewsdecoder(url, interval=1)
        if r.get("success") or r.get("status"):
            return r["decoded_url"]
        print("decode failed:", r.get("message"))
    except Exception as e:
        print("decode failed:", repr(e))
    return None

def collect():
    out, seen = [], set()
    for it in from_rss() + from_hn():
        real = resolve(it["url"])
        if not real or real in seen or any(d in real for d in SKIP_DOMAINS):
            continue
        seen.add(real)
        it["url"] = real
        out.append(it)
    for i, it in enumerate(out):
        it["id"] = i
    return out