"""
Response Parser
Extracts structured signals from raw AI engine responses:
  - Whether the brand is mentioned
  - Where it appears (sentence index = position score)
  - How many times it's mentioned
  - Sentiment context around the mention
  - Which competitors are mentioned
"""

import re
from typing import Optional


# ─── Sentiment Word Banks ────────────────────────────────────────────────────────
POSITIVE_SIGNALS = [
    "best", "top", "highly recommended", "excellent", "great", "popular",
    "trusted", "effective", "premium", "leading", "superior", "perfect",
    "ideal", "outstanding", "loved", "favorite", "highly rated", "well-reviewed",
    "number one", "#1", "gold standard", "go-to",
]

NEGATIVE_SIGNALS = [
    "avoid", "poor", "worst", "bad", "not recommended", "overpriced",
    "ineffective", "disappointing", "low quality", "cheap", "unreliable",
    "concerns", "warning", "side effects", "complaints",
]


def normalize(text: str) -> str:
    """Lowercase and strip punctuation for fuzzy matching."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def find_mention_position(sentences: list[str], brand_norm: str) -> tuple[int, str]:
    """
    Find the first sentence index containing the brand mention.

    Returns:
        (position_index, position_label)
        position_index: 0-based sentence index, -1 if not found
        position_label: human-readable label
    """
    for i, sent in enumerate(sentences):
        if brand_norm in normalize(sent):
            total = len(sentences)
            if i == 0:
                label = "1st mention (opener)"
            elif i <= 2:
                label = f"Top {i+1} sentences"
            elif i <= total // 2:
                label = f"Sentence {i+1} (upper half)"
            else:
                label = f"Sentence {i+1} (lower half)"
            return (i, label)
    return (-1, "Not Mentioned")


def extract_sentiment(response: str, brand_norm: str) -> str:
    """
    Extract sentiment in the context of the brand mention.
    Looks for positive/negative signal words near the mention.
    """
    sentences = re.split(r"[.\n]", response.lower())
    # Find sentences that mention the brand
    brand_sentences = [s for s in sentences if brand_norm in normalize(s)]

    if not brand_sentences:
        return "N/A"

    context = " ".join(brand_sentences)
    pos_hits = sum(1 for w in POSITIVE_SIGNALS if w in context)
    neg_hits = sum(1 for w in NEGATIVE_SIGNALS if w in context)

    if pos_hits > neg_hits:
        return "Positive"
    elif neg_hits > pos_hits:
        return "Negative"
    else:
        return "Neutral"


def parse_response(
    response: str,
    brand: str,
    competitors: list[str],
) -> dict:
    """
    Parse a single AI engine response for AEO signals.

    Args:
        response: Raw text response from the AI engine
        brand: Brand/product name to track
        competitors: List of competitor names to track

    Returns:
        dict with keys:
            brand_mentioned (bool)
            mention_count (int)
            position (str)        — human label
            position_index (int)  — 0-based; -1 if not found
            sentiment (str)       — Positive / Neutral / Negative / N/A
            competitor_mentions (dict[str, bool])
            raw_response (str)
    """
    brand_norm = normalize(brand)
    response_norm = normalize(response)

    # Split into sentences for position analysis
    sentences = [s.strip() for s in re.split(r"[.\n]", response) if s.strip()]

    # Brand mention
    brand_mentioned = brand_norm in response_norm

    # Mention count — count distinct occurrences
    mention_count = response_norm.count(brand_norm) if brand_mentioned else 0

    # Position
    position_index, position_label = find_mention_position(sentences, brand_norm)

    # Sentiment
    sentiment = extract_sentiment(response, brand_norm) if brand_mentioned else "N/A"

    # Competitor mentions
    competitor_mentions = {
        comp: normalize(comp) in response_norm
        for comp in competitors
    }

    return {
        "brand_mentioned": brand_mentioned,
        "mention_count": mention_count,
        "position": position_label,
        "position_index": position_index,
        "sentiment": sentiment,
        "competitor_mentions": competitor_mentions,
        "raw_response": response,
    }
