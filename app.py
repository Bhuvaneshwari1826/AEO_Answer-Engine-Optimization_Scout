"""
AEO Scout — AI Engine Optimization Diagnostic Tool
Developed by Bhuvaneshwari Appam

Simultaneously queries Claude, GPT-4o, and Gemini to measure how visible
your Amazon product is across AI shopping assistants, with actionable fix suggestions.
"""

import streamlit as st
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

from engines.claude_engine import query_claude
from engines.openai_engine import query_gpt
from engines.gemini_engine import query_gemini
from analyzer.parser import parse_response
from analyzer.scorer import compute_aeo_score, generate_recommendations
from analyzer.fix_generator import generate_listing_fixes

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AEO Scout | AI Visibility Diagnostic",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}

.main-header h1 {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.main-header p {
    color: #6b6b80;
    font-size: 1.05rem;
    margin-top: 0.5rem;
    font-family: 'DM Mono', monospace;
}

.engine-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
}

.score-pill {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

.score-a { background: #064e3b; color: #6ee7b7; }
.score-b { background: #1e3a5f; color: #93c5fd; }
.score-c { background: #451a03; color: #fcd34d; }
.score-d { background: #3b0a0a; color: #fca5a5; }

.metric-box {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
}

.metric-box .label {
    color: #6b6b80;
    font-size: 0.78rem;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-box .value {
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0.3rem 0 0 0;
}

.tag-green { color: #34d399; }
.tag-red { color: #f87171; }
.tag-yellow { color: #fbbf24; }

.rec-card {
    background: #0f0f1a;
    border-left: 3px solid #a78bfa;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    font-size: 0.93rem;
    line-height: 1.6;
}

.fix-card {
    background: #0c1a0f;
    border-left: 3px solid #34d399;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    font-size: 0.93rem;
    line-height: 1.6;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.7rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}

.stButton > button:hover {
    opacity: 0.85;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
}

.divider {
    border: none;
    border-top: 1px solid #1e1e2e;
    margin: 2rem 0;
}

.badge {
    display: inline-block;
    background: #1e1e2e;
    color: #a78bfa;
    padding: 0.15rem 0.6rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    margin-right: 0.3rem;
}

.competitor-row {
    display: flex;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #1e1e2e;
    font-size: 0.9rem;
}

.stExpander {
    background: #111118;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎯 AEO Scout</h1>
    <p>AI Engine Optimization · See where your product ranks across Claude, GPT-4o & Gemini</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─── Info Strip ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-box">
        <div class="label">Engines Queried</div>
        <div class="value">3</div>
        <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">Claude · GPT-4o · Gemini</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="metric-box">
        <div class="label">What You Get</div>
        <div class="value" style="font-size:1.4rem">Score + Fix</div>
        <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">Visibility grade & copy suggestions</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="metric-box">
        <div class="label">Avg Response Time</div>
        <div class="value">~6s</div>
        <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">Parallel API calls</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─── Input Form ─────────────────────────────────────────────────────────────────
st.markdown("### 🔎 Run Your Diagnostic")

with st.form("aeo_form"):
    col_a, col_b = st.columns(2)

    with col_a:
        query = st.text_input(
            "Shopper Query",
            placeholder="e.g.  best magnesium supplement for seniors with poor sleep",
            help="Phrase this exactly how a shopper would ask ChatGPT or Claude"
        )
        brand = st.text_input(
            "Your Brand / Product Name",
            placeholder="e.g.  Nature Made Magnesium Glycinate",
            help="Exact name as it appears on your Amazon listing"
        )

    with col_b:
        competitors_raw = st.text_input(
            "Competitor Names (comma-separated)",
            placeholder="e.g.  Thorne, Garden of Life, NOW Foods",
            help="Up to 5 competitors you want to benchmark against"
        )
        category = st.selectbox(
            "Product Category",
            ["Health & Supplements", "Electronics", "Beauty & Personal Care",
             "Home & Kitchen", "Sports & Outdoors", "Food & Grocery", "Other"],
            help="Helps tune the AI query context"
        )

    submitted = st.form_submit_button("🚀 Run AEO Diagnostic")


# ─── Query Suggestions ───────────────────────────────────────────────────────────
with st.expander("💡 Query examples by category"):
    st.markdown("""
    | Category | Example Query |
    |---|---|
    | Supplements | `best magnesium glycinate for seniors with insomnia` |
    | Electronics | `best noise cancelling headphones under 5000 rupees` |
    | Beauty | `best retinol serum for sensitive skin beginners` |
    | Kitchen | `best air fryer for small apartments 2-person household` |
    | Sports | `best creatine monohydrate for women weight training` |
    """)


# ─── System Prompt ───────────────────────────────────────────────────────────────
def build_system_prompt(cat: str) -> str:
    return (
        f"You are a helpful AI shopping assistant specializing in {cat}. "
        "When a user asks for a product recommendation, respond with 3-5 specific, "
        "named product recommendations. Include the brand name prominently. "
        "Be direct, specific, and helpful. Format: numbered list with brand + product name first."
    )


# ─── Core Diagnostic Logic ───────────────────────────────────────────────────────
def run_engine(engine_name: str, query: str, system_prompt: str) -> tuple:
    """Run a single engine query and return (name, response, error)."""
    try:
        if engine_name == "Claude":
            resp = query_claude(query, system_prompt)
        elif engine_name == "GPT-4o":
            resp = query_gpt(query, system_prompt)
        elif engine_name == "Gemini":
            resp = query_gemini(query, system_prompt)
        else:
            resp = ""
        return (engine_name, resp, None)
    except Exception as e:
        return (engine_name, "", str(e))


def run_parallel_queries(query: str, system_prompt: str) -> dict:
    """Run all three engines in parallel using ThreadPoolExecutor."""
    engines = ["Claude", "GPT-4o", "Gemini"]
    results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_engine, name, query, system_prompt): name
            for name in engines
        }
        for future in as_completed(futures):
            name, resp, err = future.result()
            results[name] = {"response": resp, "error": err}

    return results


# ─── Results ────────────────────────────────────────────────────────────────────
if submitted:
    if not query.strip() or not brand.strip():
        st.error("⚠️  Please fill in both the Shopper Query and Brand Name fields.")
        st.stop()

    competitors = [c.strip() for c in competitors_raw.split(",") if c.strip()][:5]
    system_prompt = build_system_prompt(category)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### 📡 Querying AI Engines...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Parallel query
    status_text.markdown("`→ Firing parallel requests to Claude, GPT-4o, and Gemini...`")
    start_time = time.time()

    engine_results = run_parallel_queries(query, system_prompt)

    elapsed = round(time.time() - start_time, 2)
    progress_bar.progress(50)
    status_text.markdown(f"`→ Responses received in {elapsed}s. Analyzing visibility...`")

    # Parse responses
    parsed = {}
    for engine, data in engine_results.items():
        if data["error"]:
            parsed[engine] = {
                "brand_mentioned": False,
                "position": "Error",
                "sentiment": "N/A",
                "competitor_mentions": {},
                "raw_response": f"Error: {data['error']}",
                "mention_count": 0,
                "position_index": -1,
            }
        else:
            parsed[engine] = parse_response(data["response"], brand, competitors)

    progress_bar.progress(75)
    status_text.markdown("`→ Scoring and generating recommendations...`")

    # Score
    scores = compute_aeo_score(parsed)
    recommendations = generate_recommendations(parsed, brand, competitors)

    progress_bar.progress(100)
    status_text.markdown(f"`✅ Done in {elapsed}s — report ready below`")

    # ─── Overall Score ────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## 📊 Your AEO Report Card")

    grade = scores["grade"]
    grade_color = {"A": "#34d399", "B": "#60a5fa", "C": "#fbbf24", "D": "#f87171"}
    grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🔴"}
    grade_label = {"A": "Excellent", "B": "Good", "C": "Needs Work", "D": "Invisible"}

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="label">Overall AEO Score</div>
            <div class="value" style="color:{grade_color.get(grade,'#fff')}">{scores['overall']}/100</div>
            <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">{grade_emoji.get(grade,'')} {grade_label.get(grade,'')}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="label">Grade</div>
            <div class="value" style="color:{grade_color.get(grade,'#fff')}">{grade}</div>
            <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">Across 3 AI engines</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        engines_mentioned = sum(1 for r in parsed.values() if r["brand_mentioned"])
        st.markdown(f"""
        <div class="metric-box">
            <div class="label">Engines Mentioning You</div>
            <div class="value" style="color:{'#34d399' if engines_mentioned >= 2 else '#f87171'}">{engines_mentioned}/3</div>
            <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">{'Majority coverage' if engines_mentioned >= 2 else 'Critical gap'}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        avg_pos = scores.get("avg_position_score", 0)
        st.markdown(f"""
        <div class="metric-box">
            <div class="label">Avg Position Score</div>
            <div class="value">{avg_pos}/30</div>
            <div style="font-size:0.8rem;color:#6b6b80;margin-top:0.2rem">Higher = mentioned earlier</div>
        </div>""", unsafe_allow_html=True)

    # ─── Per-Engine Breakdown ─────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Per-Engine Breakdown")

    engine_icons = {"Claude": "🟣", "GPT-4o": "🟢", "Gemini": "🔵"}
    e1, e2, e3 = st.columns(3)

    for col, (engine, result) in zip([e1, e2, e3], parsed.items()):
        escore = scores["engine_scores"][engine]
        grade_cls = f"score-{scores['engine_grades'][engine].lower()}"
        with col:
            mentioned_tag = (
                f'<span class="tag-green">✅ Mentioned</span>'
                if result["brand_mentioned"]
                else f'<span class="tag-red">❌ Not Mentioned</span>'
            )
            sentiment_color = {
                "Positive": "#34d399", "Neutral": "#fbbf24", "Negative": "#f87171", "N/A": "#6b6b80"
            }.get(result["sentiment"], "#6b6b80")

            st.markdown(f"""
            <div class="engine-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                    <span style="font-weight:700;font-size:1.05rem">{engine_icons[engine]} {engine}</span>
                    <span class="score-pill {grade_cls}">{escore}/100 · {scores['engine_grades'][engine]}</span>
                </div>
                <div style="margin-bottom:0.4rem">{mentioned_tag}</div>
                <div style="font-size:0.82rem;color:#6b6b80;margin-top:0.5rem">
                    Position: <span style="color:#e8e8f0">{result['position']}</span>
                </div>
                <div style="font-size:0.82rem;color:#6b6b80">
                    Sentiment: <span style="color:{sentiment_color}">{result['sentiment']}</span>
                </div>
                <div style="font-size:0.82rem;color:#6b6b80">
                    Mentions: <span style="color:#e8e8f0">{result['mention_count']}×</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ─── Competitor Matrix ────────────────────────────────────────────────────
    if competitors:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("### 🥊 Competitive Visibility Matrix")
        st.caption("Who shows up — and who doesn't — across AI shopping assistants")

        all_names = [brand] + competitors
        headers = ["Brand / Product", "Claude", "GPT-4o", "Gemini", "Total Coverage"]

        rows_html = ""
        for name in all_names:
            is_brand = name == brand
            row_style = "background:#1a1a2e;" if is_brand else ""
            coverage = 0
            cells = f'<td style="font-weight:{"700" if is_brand else "400"};color:{"#a78bfa" if is_brand else "#e8e8f0"}">{name}{"  ★" if is_brand else ""}</td>'
            for engine in ["Claude", "GPT-4o", "Gemini"]:
                if is_brand:
                    present = parsed[engine]["brand_mentioned"]
                else:
                    present = parsed[engine]["competitor_mentions"].get(name, False)
                coverage += 1 if present else 0
                cells += f'<td style="text-align:center">{"✅" if present else "❌"}</td>'
            bar = "█" * coverage + "░" * (3 - coverage)
            cells += f'<td style="text-align:center;font-family:monospace;color:{"#34d399" if coverage==3 else "#fbbf24" if coverage>=1 else "#f87171"}">{bar} {coverage}/3</td>'
            rows_html += f'<tr style="{row_style}">{cells}</tr>'

        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;font-size:0.9rem">
            <thead>
                <tr style="border-bottom:1px solid #1e1e2e;color:#6b6b80;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px">
                    {''.join(f'<th style="text-align:left;padding:0.6rem 0.5rem">{h}</th>' for h in headers)}
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """, unsafe_allow_html=True)

    # ─── Recommendations ──────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### 💡 Diagnostic Recommendations")

    for rec in recommendations:
        st.markdown(f'<div class="rec-card">{rec}</div>', unsafe_allow_html=True)

    # ─── AI-Powered Listing Fix (Claude) ─────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### ✍️ AI-Powered Listing Copy Fix")
    st.caption("Claude analyzes the gap and rewrites copy elements to improve AEO ranking")

    with st.spinner("Claude is generating AEO-optimized copy suggestions..."):
        missing_engines = [e for e, r in parsed.items() if not r["brand_mentioned"]]
        fixes = generate_listing_fixes(
            brand=brand,
            query=query,
            category=category,
            missing_engines=missing_engines,
            competitor_responses={e: parsed[e]["raw_response"] for e in parsed},
            score=scores["overall"],
        )

    if fixes:
        for fix in fixes:
            st.markdown(f'<div class="fix-card">{fix}</div>', unsafe_allow_html=True)
    else:
        st.info("Fix generation failed — check your ANTHROPIC_API_KEY.")

    # ─── Raw Responses ────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    with st.expander("🔍 Raw AI Responses"):
        for engine, data in engine_results.items():
            st.markdown(f"**{engine_icons[engine]} {engine}**")
            if data["error"]:
                st.error(f"Error: {data['error']}")
            else:
                st.write(data["response"])
            st.markdown("---")

    # ─── Share Strip ─────────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    summary_text = (
        f"AEO Scout Report for '{brand}'\n"
        f"Query: '{query}'\n"
        f"Overall Score: {scores['overall']}/100 (Grade {grade})\n"
        f"Engines Mentioning You: {engines_mentioned}/3\n"
        f"Claude: {scores['engine_scores']['Claude']}/100 | "
        f"GPT-4o: {scores['engine_scores']['GPT-4o']}/100 | "
        f"Gemini: {scores['engine_scores']['Gemini']}/100\n"
        f"\nGenerated by AEO Scout — github.com/bhuvaneshwariappam/aeo-scout"
    )
    st.download_button(
        "📥 Download Report (.txt)",
        data=summary_text,
        file_name=f"aeo_report_{brand.replace(' ', '_').lower()}.txt",
        mime="text/plain",
    )

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#2e2e3e;font-size:0.78rem;font-family:'DM Mono',monospace;padding-bottom:2rem">
    AEO Scout · Built with Claude + GPT-4o + Gemini · Streamlit<br>
    Bhuvaneshwari Appam · 2026
</div>
""", unsafe_allow_html=True)
