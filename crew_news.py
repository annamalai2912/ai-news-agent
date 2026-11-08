# crew_news.py
import os, json, requests, markdown
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
import trafilatura
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from news_sources import collect

llm = LLM(
    model=os.getenv("GEMINI_MODEL", "gemini/gemini-3.8-flash"),
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.2,
)

@tool("read_article")
def read_article(url: str) -> str:
    """Fetches the main text of an article URL (first ~4000 chars)."""
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html) if html else None
    return (text or "Could not fetch article.")[:4000]

def save_to_drive(md_text):
    url, secret = os.getenv("DRIVE_WEBHOOK_URL"), os.getenv("DRIVE_SECRET")
    if not (url and secret):
        print("Drive not configured; skipping upload.")
        return
    r = requests.post(url, json={
        "secret": secret,
        "title": "AI News " + datetime.now(IST).strftime("%Y-%m-%d"),
        "html": markdown.markdown(md_text),
    }, timeout=60)
    print("Drive:", r.text)

def main():
    items = collect()
    if len(items) < 10:
        raise SystemExit("Too few items collected; aborting.")
    data = json.dumps(items, ensure_ascii=False)

    researcher = Agent(
        role="AI News Researcher",
        goal="Pick the 5 most important distinct AI stories from the last 24 hours",
        backstory="You follow launches, models and research from OpenAI, Anthropic, "
                  "Google, Apple, Meta and Microsoft. You ignore minor news and merge duplicates.",
        llm=llm, verbose=True)
    analyst = Agent(
        role="AI Analyst",
        goal="Explain each story accurately and say why it matters",
        backstory="You read the source article before summarizing and never guess facts.",
        tools=[read_article], llm=llm, verbose=True)
    editor = Agent(
        role="Editor",
        goal="Produce a clean digest that uses only verified links",
        backstory="You only allow URLs that appear in the collected data and prefer official sources.",
        llm=llm, verbose=True)

    t1 = Task(
        description=("Here are candidate items from the last 24 hours (JSON):\n" + data +
                     "\n\nShortlist the 5 most important distinct stories. Prioritize major "
                     "product launches, new models, important research and big announcements. "
                     "Merge duplicates.Ignore stock, IPO, valuation and market-reaction stories unless they reflect a major company event. If fewer than 5 are important, return fewer."),
        expected_output="Up to 5 stories with title, url, source.",
        agent=researcher)
    t2 = Task(
        description=("For each shortlisted story, call read_article on its url, then write a "
                     "2-3 sentence summary and a 1-2 sentence 'Why it matters'."
                     "If read_article returns 'Could not fetch article', write the summary from the title only, "
                     "say 'Based on headline only', and do not add facts that are not in the title. "),
        expected_output="Per story: title, summary, why it matters, url.",
        agent=analyst, context=[t1])
    t3 = Task(
        description=("Write the final digest in Markdown with a heading per story, the summary, "
                     "a 'Why it matters' line, and a source link. Use only URLs from the earlier "
                     "tasks. Remove duplicates."),
        expected_output="Final Markdown digest.",
        agent=editor, context=[t1, t2])

    crew = Crew(agents=[researcher, analyst, editor], tasks=[t1, t2, t3],
                process=Process.sequential, max_rpm=8)
    import time
    for attempt in range(3):
        try:
            out = str(crew.kickoff())
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(30 * (attempt + 1))
    else:
        raise SystemExit("All attempts failed")
    print(out)
    save_to_drive(out)

if __name__ == "__main__":
    main()