"""
Sentiment Analysis Service
"""
from app.services.groq_service import groq_service

async def analyze_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of English text.
    Returns: 'positive', 'neutral', or 'negative'.
    """
    prompt = (
        f"Analyze the sentiment of this customer query: '{text}'. "
        f"Respond with exactly one word, strictly choose from: positive, neutral, negative."
    )
    
    try:
        response = await groq_service.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.0
        )
        sentiment = response.choices[0].message.content.strip().lower()
        if "negative" in sentiment:
            return "negative"
        if "positive" in sentiment:
            return "positive"
        return "neutral"
    except Exception as e:
        return "neutral"
