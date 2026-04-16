"""
FAQ helper service — parse FAQ documents into structured question/answer entries.
"""
import re
from typing import List, Dict


QA_BLOCK_PATTERN = re.compile(
    r"(?:^|\n)\s*Q(?:uestion)?\s*[:\-]\s*(.+?)\s*\n\s*A(?:nswer)?\s*[:\-]\s*(.+?)(?=\n\s*Q(?:uestion)?\s*[:\-]|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def parse_faq_entries(raw_text: str) -> List[Dict[str, str]]:
    """
    Parse an FAQ document into Q/A entries.
    Expected format:
      Q: ...
      A: ...
    """
    text = (raw_text or "").strip()
    if not text:
        return []

    entries: List[Dict[str, str]] = []
    for question, answer in QA_BLOCK_PATTERN.findall(text):
        q = " ".join(question.split())
        a = " ".join(answer.split())
        if q and a:
            entries.append({"question": q, "answer": a})

    return entries
