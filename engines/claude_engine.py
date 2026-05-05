"""
Claude Engine
Queries Anthropic's Claude (claude-opus-4-5) for product recommendations.
"""

import anthropic
import os


def query_claude(user_query: str, system_prompt: str) -> str:
    """
    Query Claude with a shopper's product question.

    Args:
        user_query: The natural-language shopping query (e.g. "best magnesium for seniors")
        system_prompt: Role/context prompt defining Claude's persona

    Returns:
        Claude's text response as a string.

    Raises:
        anthropic.APIError: On API failures (rate limit, auth, etc.)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_query}
        ],
    )

    return message.content[0].text
