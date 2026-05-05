"""
OpenAI GPT-4o Engine
Queries OpenAI's GPT-4o for product recommendations.
"""

from openai import OpenAI
import os


def query_gpt(user_query: str, system_prompt: str) -> str:
    """
    Query GPT-4o with a shopper's product question.

    Args:
        user_query: The natural-language shopping query
        system_prompt: System-level context for the assistant role

    Returns:
        GPT-4o's text response as a string.

    Raises:
        openai.OpenAIError: On API failures (rate limit, auth, etc.)
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=600,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
    )

    return response.choices[0].message.content
