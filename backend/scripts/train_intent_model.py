"""
Train a simple scikit-learn intent router from FAQ dataset.

Usage:
  python backend/scripts/train_intent_model.py \
      --dataset backend/data/faq_dataset.json \
      --output backend/models/intent_router.joblib
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="backend/data/faq_dataset.json")
    parser.add_argument("--output", default="backend/models/intent_router.joblib")
    return parser.parse_args()


def load_dataset(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("faqs", [])
    if not isinstance(raw, list):
        raise ValueError("Dataset must be a list of FAQ objects.")
    return raw


def build_training_rows(entries):
    texts = []
    labels = []
    for item in entries:
        question = str(item.get("question", "")).strip()
        category = str(item.get("category", "general")).strip() or "general"
        if not question:
            continue
        texts.append(question)
        labels.append(category.lower())
        for kw in item.get("keywords", []) or []:
            keyword = str(kw).strip()
            if keyword:
                texts.append(keyword)
                labels.append(category.lower())
    if len(set(labels)) < 2:
        raise ValueError("Need at least two intent classes to train model.")
    return texts, labels


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entries = load_dataset(dataset_path)
    texts, labels = build_training_rows(entries)

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=2000)),
        ]
    )
    pipeline.fit(texts, labels)
    joblib.dump(pipeline, output_path)

    print(f"Trained intent router with {len(texts)} rows and {len(set(labels))} labels.")
    print(f"Saved model to: {output_path}")


if __name__ == "__main__":
    main()

