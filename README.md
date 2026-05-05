# 🎯 AEO (Answer Engine Optimization) Scout

**AI Engine Optimization Diagnostic for Amazon Sellers**

> *In 2026, the search landscape has shifted from traditional indexing to conversational LLMs like ChatGPT, Claude, and Gemini. AEO Scout provides the observability you need to track your product’s presence in these AI responses and offers the specific technical adjustments required to fix visibility gaps.*

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Claude](https://img.shields.io/badge/Claude-claude--opus--4--5-7c3aed)](https://anthropic.com)
[![GPT-4o](https://img.shields.io/badge/OpenAI-GPT--4o-10a37f)](https://openai.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini%201.5%20Pro-4285F4)](https://deepmind.google/gemini)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 What Is AEO Scout?

**AEO (Answer Engine Optimization)** is what SEO was in 2005 — the next frontier for product discoverability.

When a shopper types *"best magnesium supplement for seniors"* into Claude, GPT-4o, or Gemini, these AI engines synthesize their training data and surface specific product recommendations. Most Amazon sellers have **no idea** whether they're being mentioned, where they rank, or why their competitors are winning.

AEO Scout solves this. In ~6 seconds, it:

1. **Fires the shopper query simultaneously** to Claude, GPT-4o, and Gemini
2. **Parses each response** — brand mention, position, sentiment, competitor coverage
3. **Scores your AEO health** per engine and overall (0–100 with letter grade)
4. **Generates a competitive matrix** showing you vs. up to 5 competitors across all three engines
5. **Writes AI-powered listing copy fixes** (via Claude) with real example text you can copy-paste

---

## 🖼️ Screenshots

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎯 AEO Scout                                                               │
│  AI Engine Optimization · Claude + GPT-4o + Gemini                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  Shopper Query: "best magnesium supplement for seniors with poor sleep"      │
│  Brand: Nature Made Magnesium Glycinate                                     │
│  Competitors: Thorne, Garden of Life, NOW Foods                             │
│                                                ↓ Run Diagnostic             │
├──────────────────────┬──────────────────────┬──────────────────────────────┤
│  Overall AEO Score   │  Grade               │  Engines Mentioning You      │
│      72/100          │    B                 │         2/3                  │
├──────────────────────┼──────────────────────┼──────────────────────────────┤
│  🟣 Claude: 85/100 A │  🟢 GPT-4o: 65/100 B │  🔵 Gemini: 50/100 C        │
│  ✅ Mentioned        │  ✅ Mentioned         │  ❌ Not Mentioned            │
│  Position: Sent. 1   │  Position: Sent. 4   │  Sentiment: N/A              │
├──────────────────────┴──────────────────────┴──────────────────────────────┤
│  Competitive Matrix                                                          │
│  Brand/Product          Claude    GPT-4o    Gemini    Coverage              │
│  Nature Made ★          ✅        ✅        ❌        ██░ 2/3               │
│  Thorne                 ✅        ✅        ✅        ███ 3/3               │
│  Garden of Life         ❌        ✅        ✅        ██░ 2/3               │
│  NOW Foods              ❌        ❌        ✅        █░░ 1/3               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
aeo-scout/
│
├── app.py                        # Streamlit entry point — UI, form, orchestration
│
├── engines/                      # One module per AI engine
│   ├── __init__.py
│   ├── claude_engine.py          # Anthropic claude-opus-4-5
│   ├── openai_engine.py          # OpenAI gpt-4o
│   └── gemini_engine.py          # Google gemini-1.5-pro
│
├── analyzer/                     # Intelligence layer
│   ├── __init__.py
│   ├── parser.py                 # Brand mention · position · sentiment · competitor scan
│   ├── scorer.py                 # AEO score (0-100) · letter grade · recommendations
│   └── fix_generator.py          # Claude-powered listing copy fix generation
│
├── .streamlit/
│   ├── config.toml               # Theme (dark, purple accent)
│   └── secrets.toml.example      # API key template
│
├── .env.example                  # Local dev key template
├── .gitignore
├── requirements.txt
├── README.md
├── DEPLOY.md
└── PROJECT_DEEP_DIVE.md
```

### Data Flow

```
User Input (query + brand + competitors)
         │
         ▼
  ThreadPoolExecutor (3 workers, parallel)
    ┌────────┬────────┬────────┐
    │ Claude │ GPT-4o │ Gemini │
    └────────┴────────┴────────┘
         │
         ▼
  parser.parse_response() × 3
  → brand_mentioned, position_index, sentiment, competitor_mentions
         │
         ▼
  scorer.compute_aeo_score()
  → engine_scores, engine_grades, overall, grade
         │
         ├──→ scorer.generate_recommendations()  → 3-5 prioritized fixes
         │
         └──→ fix_generator.generate_listing_fixes()  → Claude rewrites listing copy
         │
         ▼
  Streamlit renders: Report Card · Engine Cards · Competitor Matrix
                     Recommendations · AI Copy Fixes · Download Button
```

---

## ⚙️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| UI / App | Streamlit | Ship fast. No frontend build step. Looks great with custom CSS |
| Engine 1 | Anthropic `claude-opus-4-5` | Best reasoning + used for fix generation |
| Engine 2 | OpenAI `gpt-4o` | Most widely used consumer AI, critical for AEO coverage |
| Engine 3 | Google `gemini-1.5-pro` | Google's AI — increasingly used in Shopping queries |
| Concurrency | `ThreadPoolExecutor` (stdlib) | Parallel API calls; cuts 18s serial time → ~6s |
| NLP | Pure Python string ops | No heavy ML lib needed; keeps cold-start fast |
| Secrets | `python-dotenv` + Streamlit secrets | Dual-mode: local `.env` + cloud `secrets.toml` |

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.10+
- API keys for: Anthropic, OpenAI, Google AI Studio

### 1. Clone

```bash
git clone https://github.com/bhuvaneshwariappam/aeo-scout.git
cd aeo-scout
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up API keys

```bash
cp .env.example .env
# Edit .env and paste your keys:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=AIza...
```

### 4. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🔑 Getting API Keys

| Provider | Where to get | Free tier? |
|---|---|---|
| Anthropic | https://console.anthropic.com | $5 free credit |
| OpenAI | https://platform.openai.com/api-keys | $5 free credit |
| Google (Gemini) | https://aistudio.google.com/app/apikey | Free tier available |

> **Cost per diagnostic run:** ~$0.02–0.05 total across all three engines for typical queries.

---

## 📐 Scoring Rubric

Each engine is scored 0–100 independently:

| Signal | Points |
|---|---|
| Brand mentioned at all | +50 |
| Mentioned in sentences 1–2 (top position) | +30 |
| Mentioned in sentences 3–4 | +15 |
| Mentioned in sentence 5+ | +5 |
| Positive sentiment in mention context | +20 |
| Neutral sentiment | +10 |
| Mentioned 2+ times (frequency bonus) | +5 |

**Overall score** = average of three engine scores.

**Grades:**
- 🟢 A (80–100): Strong AEO — you're showing up early and positively
- 🔵 B (60–79): Good — mentioned but room to improve position/sentiment
- 🟡 C (40–59): Weak — mentioned sporadically or very late
- 🔴 D (0–39): Critical — largely invisible to AI shopping assistants

---

## 💡 Why AEO Matters for Amazon Sellers

The shift is happening fast:

- **28% of US adults** now use AI assistants (ChatGPT, Claude, Gemini) for product research (2025 data)
- Amazon's own AI assistant **Rufus** synthesizes listing data and reviews to answer shopper questions
- Traditional SEO (Google keyword ranking) is declining as AI-generated answers replace search results pages
- Sellers who optimize their listings for **natural-language query matching** will own the next decade of e-commerce

AEO Scout gives sellers their first visibility report card across the AI search landscape.

---

## 🗺️ Roadmap (further improvements)

- [ ] **Weekly tracking** — run the same query every 7 days, show score trend over time
- [ ] **ASIN import** — paste an Amazon URL, auto-extract brand + competitor names
- [ ] **Amazon Rufus simulation** — query Amazon's own AI assistant for category coverage
- [ ] **Bulk mode** — run 10 queries at once, get a full AEO audit
- [ ] **Slack/email alerts** — notify when your AEO score drops below threshold
- [ ] **Export to PDF** — one-click shareable report for brands and agencies

---

## 🙋 About the Author

Built by **Bhuvaneshwari Appam**

- GitHub: [github.com/bhuvaneshwari1826](https://github.com/bhuvaneshwari1826)
- LinkedIn: [linkedin.com/in/bhuvaneshwariappam](https://linkedin.com/in/bhuvaneshwariappam)
- Email: bhuvaneshwariappam@gmail.com

---

## 📄 License

MIT — use it, extend it, ship it.
