"""
Intent router service (scikit-learn).
Predicts category + confidence for a user query to support routing/handoff logic.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Dict, Any

import joblib
import re

from app.config import settings
from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)


class IntentRouterService:
    def __init__(self) -> None:
        self.enabled = bool(settings.ENABLE_INTENT_ROUTER)
        self.model_path = Path(settings.INTENT_MODEL_PATH)
        self._pipeline = None
        self._loaded = False

    def _load_if_needed(self) -> None:
        if self._loaded:
            return
        self._loaded = True

        if not self.enabled:
            logger.info("Intent router disabled by config.")
            return
        if not self.model_path.exists():
            logger.warning("Intent router model not found at %s", self.model_path)
            return

        try:
            self._pipeline = joblib.load(self.model_path)
            logger.info("Intent router model loaded from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load intent router model: %s", e)
            self._pipeline = None

    def predict(self, text: str) -> Optional[Dict[str, Any]]:
        self._load_if_needed()
        if not self._pipeline or not text.strip():
            return None

        try:
            probs = self._pipeline.predict_proba([text])[0]
            classes = self._pipeline.classes_
            idx = int(probs.argmax())
            label = str(classes[idx])
            confidence = float(probs[idx])
            return {"label": label, "confidence": confidence}
        except Exception as e:
            logger.error("Intent prediction failed: %s", e)
            return None

    async def extract_order_id(self, text: str) -> Optional[str]:
        """
        Uses Regex to extract an order ID from the text if it exists.
        Returns the order ID (e.g. ORD-5001) or None.
        """
        try:
            # Look for explicit exact matching patterns (ORD-XXXX)
            match = re.search(r'ORD-\d{4,}', text, re.IGNORECASE)
            if match:
                return match.group(0).upper()
            return None
        except Exception as e:
            logger.error("Failed to extract order ID via regex: %s", e)
            return None


intent_router_service = IntentRouterService()
