"""
Language translation service for AI Chatbot.
Only supports English and Hindi as per requirements.
"""
from app.services.groq_service import groq_service

async def detect_and_translate_to_english(text: str) -> tuple[str, str]:
    """
    Detects if the language is English or Hindi.
    Translates to English if it's Hindi.
    Returns: (detected_language, translated_to_english_text)
    """
    prompt = (
        f"Analyze the following text. If it is in Hindi (or Hinglish), translate it to English. "
        f"If it is already in English, return it exactly as is. "
        f"Respond ONLY with a JSON array in the exact format: [\"en\" or \"hi\", \"translated or original text in English\"]. "
        f"Text to analyze: \"{text}\""
    )
    
    try:
        response = await groq_service.client.chat.completions.create(
            model="llama3-8b-8192",  # Fast model for utilities
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.0
        )
        result = response.choices[0].message.content.strip()
        import json
        import re
        
        # Extract json array in case LLM added extra text
        match = re.search(r'\[.*\]', result, re.DOTALL)
        if match:
            lang, eng_text = json.loads(match.group(0))
            # clamp to 'en' or 'hi'
            lang = 'hi' if lang.lower() == 'hi' else 'en'
            return lang, eng_text
            
        return "en", text
    except Exception as e:
        return "en", text

async def translate_to_language(text: str, target_lang: str) -> str:
    """
    Translates English text to target_lang (hi or en).
    """
    if target_lang == "en":
        return text
        
    prompt = (
        f"Translate the following English text to Hindi. "
        f"Maintain a polite, professional customer service tone. "
        f"Return ONLY the translated text, without formatting or quotes.\n\n"
        f"Text: \"{text}\""
    )
    
    try:
        response = await groq_service.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return text
