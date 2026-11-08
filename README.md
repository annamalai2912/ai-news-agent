# 🤖 Autonomous Daily AI News Agent

An autonomous multi-agent pipeline built with **CrewAI** and **Google Gemini** that curates, analyzes, and synthesizes the top AI breakthroughs every 24 hours—delivering a Markdown executive briefing directly to Google Drive daily at 5:00 AM IST.

---

## 🚀 Overview

Keeping up with fast-moving AI developments across labs, research papers, and releases is time-consuming. This autonomous system runs on a cloud cron schedule to:

1. **Ingest & Filter**: Aggregates official engineering blogs (OpenAI, Google, DeepMind, Hugging Face), Google News, and top-ranking Hacker News discussions.
2. **Decode & Clean**: Resolves redirect URLs, decodes Google News tracking links, and filters out noise, financial clickbait, and duplicate announcements.
3. **Multi-Agent Synthesis**: Deploys a specialized CrewAI team to research, deeply read source articles, and draft executive summaries explaining *why each story matters*.
4. **Cloud Delivery**: Formats the briefing and pushes it automatically into a designated Google Drive folder via a secure webhook.

---

## 🧠 Multi-Agent Architecture

```
                      ┌─────────────────────────┐
                      │ News Ingestion Pipeline │
                      │  (RSS + Google + HN)    │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   AI News Researcher    │
                      │  Shortlists top stories │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │       AI Analyst        │
                      │ Reads source & analyzes │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │         Editor          │
                      │ Formats Markdown digest │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   Google Drive Webhook  │
                      │  Daily Executive Doc    │
                      └─────────────────────────┘
```

- **Agent 1: AI News Researcher**: Scans candidate items from the last 24 hours, eliminates duplicates, and shortlists the top 5 most consequential technical announcements.
- **Agent 2: AI Analyst**: Calls custom browser tools (`read_article`) to inspect full article text, summarizing key findings and analyzing enterprise/industry impact.
- **Agent 3: Editor**: Assembles a clean, structured Markdown digest containing only verified links and high-signal takeaways.

---

## 🛠️ Tech Stack

- **Framework**: [CrewAI](https://crewai.com)
- **LLM**: [Google Gemini 3.5 Flash Lite](https://ai.google.dev/) (high throughput, ultra-low latency)
- **Extraction & Scraping**: Trafilatura, Feedparser, Google News URL Decoder
- **CI/CD & Automation**: GitHub Actions (`cron: "15 23 * * *"`)
- **Destination**: Google Apps Script & Google Drive API

---

## 📦 Getting Started

### Prerequisites

- Python 3.13+
- Gemini API Key

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/ai-news-agent.git
   cd ai-news-agent
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini/gemini-3.5-flash-lite
   DRIVE_WEBHOOK_URL=your_google_apps_script_url
   DRIVE_SECRET=your_secret_passphrase
   ```

4. **Run the agent locally:**
   ```bash
   python crew_news.py
   ```

---

## ⏰ Automated GitHub Actions Workflow

The repository includes a production-ready workflow [`.github/workflows/news.yml`](.github/workflows/news.yml) scheduled at **23:15 UTC (4:45 AM IST)**.

### Setting Up GitHub Repository Secrets

Configure the following secrets under **Settings → Secrets and variables → Actions**:

- `GEMINI_API_KEY`: Your Google Gemini API key.
- `DRIVE_WEBHOOK_URL`: Your Google Apps Script Web App URL.
- `DRIVE_SECRET`: Secret passphrase verified by the Web App.

---

## 📄 License

MIT License. Feel free to fork and adapt for your own daily intelligence workflows!
