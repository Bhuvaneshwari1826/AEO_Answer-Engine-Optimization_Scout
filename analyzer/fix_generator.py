"""
Fix Generator
Uses Claude to analyze the visibility gap and generate
AEO-optimized listing copy suggestions for the seller.
"""

import anthropic
import os


def generate_listing_fixes(
    brand: str,
    query: str,
    category: str,
    missing_engines: list[str],
    competitor_responses: dict,
    score: int,
) -> list[str]:
    """
    Ask Claude to generate concrete listing copy fixes based on the AEO diagnostic.

    Args:
        brand: The seller's brand/product name
        query: The shopper query that was tested
        category: Product category
        missing_engines: List of AI engines that did NOT mention the brand
        competitor_responses: Raw responses from each engine (to show what competitors said)
        score: The overall AEO score (0-100)

    Returns:
        List of HTML-formatted fix strings for display in Streamlit.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Build context summary of competitor responses for Claude
    competitor_context = "\n\n".join(
        f"**{engine} said:**\n{resp[:600]}"
        for engine, resp in competitor_responses.items()
        if resp
    )

    missing_str = (
        f"{brand} was NOT mentioned by: {', '.join(missing_engines)}."
        if missing_engines
        else f"{brand} was mentioned by all engines, but ranking and sentiment need improvement."
    )

    prompt = f"""You are an Amazon listing optimization expert specializing in AEO (Answer Engine Optimization).

A seller ran an AEO diagnostic for their product. Here are the results:

Product: {brand}
Category: {category}
Shopper Query Tested: "{query}"
Overall AEO Score: {score}/100
Visibility Gap: {missing_str}

Here is what the AI engines actually said when answering this query (showing which products they DID mention):
{competitor_context}

Based on this data, generate exactly 3 specific, actionable listing copy fixes. Each fix should:
1. Be concrete — give actual example copy, not just advice
2. Be specific to this brand and query
3. Explain WHY it will improve AEO ranking on the engines that missed it

Format your response as exactly 3 fixes, each starting with:
FIX 1: [Title]
[Explanation + example copy]

FIX 2: [Title]
[Explanation + example copy]

FIX 3: [Title]
[Explanation + example copy]

Be specific. Give real example text the seller can copy-paste."""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text

        # Parse the 3 fixes
        fixes = []
        for i in range(1, 4):
            start_tag = f"FIX {i}:"
            end_tag = f"FIX {i+1}:" if i < 3 else None

            start_idx = raw.find(start_tag)
            if start_idx == -1:
                continue
            end_idx = raw.find(end_tag) if end_tag else len(raw)
            if end_idx == -1:
                end_idx = len(raw)

            chunk = raw[start_idx:end_idx].strip()

            # Extract title and body
            lines = chunk.split("\n", 1)
            title_line = lines[0].replace(start_tag, "").strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            # Format as HTML
            fix_html = (
                f"<strong>🔧 Fix {i}: {title_line}</strong><br>"
                f"<span style='color:#9ca3af;font-size:0.88rem'>{body.replace(chr(10), '<br>')}</span>"
            )
            fixes.append(fix_html)

        return fixes if fixes else [
            "<strong>Fix generation returned no structured output.</strong> "
            "Check your ANTHROPIC_API_KEY and try again."
        ]

    except Exception as e:
        return [f"<strong>Fix generation error:</strong> {str(e)}"]
