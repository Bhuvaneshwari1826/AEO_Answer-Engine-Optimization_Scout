"""
AEO Scorer
Converts parsed engine results into a 0-100 score, letter grade,
and a ranked list of diagnostic recommendations.

Scoring rubric (per engine, max 100):
  ┌───────────────────────────┬────────┐
  │ Signal                    │ Points │
  ├───────────────────────────┼────────┤
  │ Brand mentioned           │  50    │
  │ Early position (sent 1-2) │  30    │
  │ Mid position (sent 3-4)   │  15    │
  │ Late position (5+)        │   5    │
  │ Positive sentiment        │  20    │
  │ Neutral sentiment         │  10    │
  │ Mentioned 2+ times        │   5    │ (bonus, capped at 5)
  └───────────────────────────┴────────┘

Overall score = simple average of the three engine scores.
Grade: A ≥ 80, B ≥ 60, C ≥ 40, D < 40
"""

from typing import Optional


def score_engine(result: dict) -> int:
    """Score a single engine result. Returns 0-100."""
    score = 0

    if not result["brand_mentioned"]:
        return 0

    # Mentioned at all: base points
    score += 50

    # Position bonus
    idx = result.get("position_index", -1)
    if idx == 0 or idx == 1:
        score += 30
    elif idx == 2 or idx == 3:
        score += 15
    elif idx >= 4:
        score += 5

    # Sentiment bonus
    sentiment = result.get("sentiment", "N/A")
    if sentiment == "Positive":
        score += 20
    elif sentiment == "Neutral":
        score += 10
    # Negative: 0

    # Frequency bonus (mentioned multiple times)
    if result.get("mention_count", 0) >= 2:
        score += 5

    return min(score, 100)


def letter_grade(score: int) -> str:
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "D"


def compute_aeo_score(parsed_results: dict) -> dict:
    """
    Compute per-engine scores, overall score, and grades.

    Args:
        parsed_results: dict of engine_name -> parse_response() output

    Returns:
        {
            engine_scores: {engine: int},
            engine_grades: {engine: str},
            overall: int,
            grade: str,
            avg_position_score: int,
        }
    """
    engine_scores = {}
    position_scores = []

    for engine, result in parsed_results.items():
        s = score_engine(result)
        engine_scores[engine] = s

        # Separate position score for display
        idx = result.get("position_index", -1)
        if idx == 0 or idx == 1:
            position_scores.append(30)
        elif idx == 2 or idx == 3:
            position_scores.append(15)
        elif idx >= 4:
            position_scores.append(5)
        else:
            position_scores.append(0)

    engine_grades = {e: letter_grade(s) for e, s in engine_scores.items()}
    overall = round(sum(engine_scores.values()) / len(engine_scores))
    avg_pos = round(sum(position_scores) / len(position_scores)) if position_scores else 0

    return {
        "engine_scores": engine_scores,
        "engine_grades": engine_grades,
        "overall": overall,
        "grade": letter_grade(overall),
        "avg_position_score": avg_pos,
    }


def generate_recommendations(
    parsed_results: dict,
    brand: str,
    competitors: list[str],
) -> list[str]:
    """
    Generate a ranked list of actionable AEO improvement recommendations.

    Checks for:
      1. Completely invisible on one or more engines → highest priority
      2. Mentioned late (low position score) → mid priority
      3. Negative sentiment → mid priority
      4. Competitors outperforming on specific engines → opportunity alert
      5. Generic AEO best-practice tip → always included
    """
    recs = []

    # 1. Invisibility alert
    not_mentioned = [e for e, r in parsed_results.items() if not r["brand_mentioned"]]
    if not_mentioned:
        engines_str = ", ".join(not_mentioned)
        recs.append(
            f"🚨 <strong>Critical:</strong> <em>{brand}</em> is completely invisible on "
            f"<strong>{engines_str}</strong>. These AI engines have zero signal for your product. "
            f"Add an FAQ section to your Amazon listing that mirrors the exact natural-language "
            f"phrasing shoppers use — AI engines index this content heavily."
        )

    # 2. Late-position warning
    late_engines = [
        e for e, r in parsed_results.items()
        if r["brand_mentioned"] and r.get("position_index", -1) >= 4
    ]
    if late_engines:
        recs.append(
            f"⬆️ <strong>Improve Position:</strong> You're mentioned late on "
            f"{', '.join(late_engines)}. Being in the first 1-2 sentences dramatically increases "
            f"click-through when AI engines surface your product. Front-load your listing title "
            f"and bullet points with category keywords + use cases."
        )

    # 3. Negative sentiment flag
    neg_engines = [
        e for e, r in parsed_results.items()
        if r.get("sentiment") == "Negative"
    ]
    if neg_engines:
        recs.append(
            f"⚠️ <strong>Sentiment Alert:</strong> The context around your brand on "
            f"{', '.join(neg_engines)} contains negative signals. Audit your reviews for "
            f"recurring complaints — AI engines synthesize review content. Address top "
            f"complaints directly in your listing A+ content."
        )

    # 4. Competitor opportunity
    if competitors:
        competitor_coverage = {}
        for comp in competitors:
            count = sum(1 for r in parsed_results.values() if r["competitor_mentions"].get(comp))
            competitor_coverage[comp] = count

        top_competitor = max(competitor_coverage, key=competitor_coverage.get)
        top_count = competitor_coverage[top_competitor]

        if top_count >= 2:
            recs.append(
                f"💡 <strong>Competitor Insight:</strong> <em>{top_competitor}</em> appears "
                f"across {top_count}/3 AI engines. Study their listing — specifically the "
                f"product title format, bullet point structure, and A+ content headers. "
                f"These are the signals AI engines are picking up."
            )

    # 5. Always-on best practice
    recs.append(
        "📝 <strong>AEO Best Practice:</strong> Add a 'Frequently Asked Questions' section "
        "to your listing using verbatim shopper language (e.g. 'Is this safe for seniors?', "
        "'Does it dissolve easily?'). AI engines like Claude and Gemini are trained to match "
        "natural-language queries — your FAQ is free AEO real estate."
    )

    return recs
