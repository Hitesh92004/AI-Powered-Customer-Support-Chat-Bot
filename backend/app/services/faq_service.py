"""
FAQ helper service — parse FAQ documents into structured question/answer entries.
"""
import csv
import json
import re
from pathlib import Path
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


def load_faq_entries_from_dataset(dataset_path: str) -> List[Dict[str, str]]:
    """
    Load FAQ entries from a server-side dataset file.
    Supported formats: .json, .jsonl, .csv, .txt
    """
    path = Path((dataset_path or "").strip())
    if not path.exists() or not path.is_file():
        raise ValueError(f"FAQ dataset file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_from_json(path)
    if suffix == ".jsonl":
        return _load_from_jsonl(path)
    if suffix == ".csv":
        return _load_from_csv(path)
    if suffix == ".txt":
        return parse_faq_entries(path.read_text(encoding="utf-8"))

    raise ValueError("Unsupported FAQ dataset format. Use .json, .jsonl, .csv, or .txt.")


def _normalize_qa(item: Dict[str, str]) -> Dict[str, str] | None:
    question = (item.get("question") or "").strip()
    answer = (item.get("answer") or "").strip()
    if not question or not answer:
        return None
    return {"question": " ".join(question.split()), "answer": " ".join(answer.split())}


def _load_from_json(path: Path) -> List[Dict[str, str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("faqs", [])
    if not isinstance(raw, list):
        raise ValueError("JSON dataset must be a list of objects with question/answer fields.")

    entries: List[Dict[str, str]] = []
    for item in raw:
        if isinstance(item, dict):
            normalized = _normalize_qa(item)
            if normalized:
                entries.append(normalized)
    return entries


def _load_from_jsonl(path: Path) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            normalized = _normalize_qa(item)
            if normalized:
                entries.append(normalized)
    return entries


def _load_from_csv(path: Path) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            normalized = _normalize_qa(row)
            if normalized:
                entries.append(normalized)
    return entries
