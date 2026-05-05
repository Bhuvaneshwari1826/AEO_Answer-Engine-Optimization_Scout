"""
Google Gemini Engine
Queries Google's Gemini 1.5 Pro for product recommendations.
"""

import google.generativeai as genai
import os


def query_gemini(user_query: str, system_prompt: str) -> str:
    """
    Query Gemini 1.5 Pro with a shopper's product question.

    Args:
        user_query: The natural-language shopping query
        system_prompt: Context prepended to user query (Gemini has no system role)

    Returns:
        Gemini's text response as a string.

    Raises:
        google.api_core.exceptions.GoogleAPIError: On API failures
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        system_instruction=system_prompt,
    )

    try:
        response = model.generate_content(
            user_query,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=600,
                temperature=0.7,
            ),
        )
        
        # Check if the response was blocked by safety filters
        if response.candidates:
            return response.text
        else:
            return "Response blocked by safety filters or empty."
            
    except Exception as e:
        # Re-raise or handle specific API errors
        print(f"API Error: {e}")
        raise

