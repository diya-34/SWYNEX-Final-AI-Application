"""
SWYNEX Final AI Application - Text Classification Module
Implements machine-learning and transparent rule-based text classification
into academic categories: Exam, Assignment, Event, Placement, Internship, Holiday, General.
Uses TF-IDF + Logistic Regression with calibrated confidence and transparent keyword fallback.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


# Supported target categories
CATEGORIES: List[str] = [
    "Exam",
    "Assignment",
    "Event",
    "Placement",
    "Internship",
    "Holiday",
    "General",
]

# Auditable keyword baseline map for transparent classification & cold-start fallback
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Exam": [
        "exam", "examination", "timetable", "time table", "hall ticket", "admit card",
        "seating arrangement", "re-evaluation", "re-checking", "backlog", "supplementary",
        "mid-term", "mid-semester", "end-term", "end-semester", "viva voce", "viva",
        "invigilation", "answer script", "remedial test", "scribe", "debarment", "debarred"
    ],
    "Assignment": [
        "assignment", "homework", "problem set", "submission", "submit", "turnitin",
        "plagiarism", "lab report", "project report", "github repository", "deliverable",
        "code submission", "canvas", "classroom", "lms", "due date", "mini-project"
    ],
    "Event": [
        "event", "hackathon", "workshop", "seminar", "webinar", "guest lecture",
        "auditions", "cultural fest", "tech fest", "symposium", "conference",
        "competition", "sports meet", "tournament", "auditorium", "tedx", "rhythm",
        "summit", "keynote", "e-summit"
    ],
    "Placement": [
        "placement", "recruitment", "campus drive", "job offer", "shortlisted",
        "ctc", "lpa", "aptitude test", "coding assessment", "technical interview",
        "hr interview", "cdc", "placement cell", "tcs", "microsoft", "google hiring",
        "amazon hiring", "deloitte", "goldman sachs", "accenture", "infosys", "barclays"
    ],
    "Internship": [
        "internship", "stipend", "summer intern", "winter intern", "industrial training",
        "trainee", "research internship", "intern", "iisc intern", "drdo intern",
        "gsoc", "remote internship", "ugrip", "isro"
    ],
    "Holiday": [
        "holiday", "closed", "closure", "suspended", "vacation", "break",
        "dussehra", "diwali", "eid", "christmas", "public holiday", "heavy rainfall",
        "cyclone alert", "weather advisory", "emergency closure", "classes resume",
        "republic day", "non-working day"
    ],
    "General": [
        "notice", "circular", "library", "mess fee", "hostel", "id card", "smart card",
        "wifi", "wi-fi", "maintenance", "lost and found", "bonafide certificate",
        "parking sticker", "scholarship", "administrative", "canteen", "bus concession",
        "health checkup", "gymnasium", "inspection"
    ],
}


class AnnouncementClassifier:
    """
    Hybrid Machine-Learning and Rule-Based Announcement Classifier.
    Uses TF-IDF + Logistic Regression with calibrated confidence and
    transparent keyword fallback for resilient operation.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else self._get_default_model_path()
        self.pipeline: Optional[Pipeline] = None
        self._load_or_train()

    def _get_default_model_path(self) -> Path:
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / "models" / "announcement_classifier.joblib"

    def _get_default_data_path(self) -> Path:
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / "data" / "sample_announcements.csv"

    def _load_or_train(self) -> None:
        """Loads serialized model if present, otherwise trains on default dataset."""
        if self.model_path.exists():
            try:
                self.pipeline = joblib.load(self.model_path)
                return
            except Exception:
                # If corrupt or version mismatch, retrain
                pass

        # Train new model from sample dataset
        data_path = self._get_default_data_path()
        if data_path.exists():
            df = pd.read_csv(data_path)
            self.train(df["text"].tolist(), df["category"].tolist())
        else:
            self.pipeline = None

    def train(self, texts: List[str], labels: List[str]) -> None:
        """Trains TF-IDF + Logistic Regression classifier and serializes pipeline."""
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=2500,
                sublinear_tf=True,
                stop_words="english",
            )),
            ("clf", LogisticRegression(
                C=1.5,
                max_iter=300,
                class_weight="balanced",
                random_state=42
            )),
        ])
        pipeline.fit(texts, labels)
        self.pipeline = pipeline

        # Save model to disk
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            joblib.dump(pipeline, self.model_path)
        except Exception:
            pass

    def _match_keywords(self, text: str) -> Dict[str, List[str]]:
        """Identifies domain keywords present in text for each category."""
        matched: Dict[str, List[str]] = {}
        text_lower = text.lower()
        for cat, keywords in CATEGORY_KEYWORDS.items():
            hits = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text_lower)]
            if hits:
                matched[cat] = hits
        return matched

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classifies announcement text into academic categories.

        Returns:
            Dictionary containing:
            - category: predicted category name
            - confidence: calibrated probability score (0.0 to 1.0)
            - probabilities: dictionary mapping all categories to probabilities
            - method: 'machine_learning' or 'rule_fallback'
            - matching_keywords: list of detected category-specific keywords
            - explanation: transparent justification for prediction
        """
        if not text or not text.strip():
            return {
                "category": "General",
                "confidence": 0.0,
                "probabilities": {c: round(1.0 / len(CATEGORIES), 3) for c in CATEGORIES},
                "method": "default_fallback",
                "matching_keywords": [],
                "explanation": "Input text was empty; defaulted safely to General category.",
            }

        cleaned_text = text.strip()
        kw_matches = self._match_keywords(cleaned_text)

        # Machine Learning Inference if pipeline is ready
        if self.pipeline is not None:
            try:
                classes = list(self.pipeline.classes_)
                proba = self.pipeline.predict_proba([cleaned_text])[0]
                prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, proba)}

                # Fill any missing category keys
                for cat in CATEGORIES:
                    if cat not in prob_dict:
                        prob_dict[cat] = 0.0

                top_idx = int(np.argmax(proba))
                top_cat = classes[top_idx]
                top_conf = round(float(proba[top_idx]), 4)

                # Heuristic safety check: if ML confidence is low and keyword matching has strong signal
                if top_conf < 0.35 and kw_matches:
                    best_kw_cat = max(kw_matches.keys(), key=lambda k: len(kw_matches[k]))
                    top_cat = best_kw_cat
                    prob_dict[best_kw_cat] = max(prob_dict.get(best_kw_cat, 0.0), 0.65)
                    # Re-normalize probabilities
                    total_p = sum(prob_dict.values())
                    if total_p > 0:
                        prob_dict = {c: round(float(p / total_p), 4) for c, p in prob_dict.items()}
                    top_conf = prob_dict[top_cat]

                # Gibberish / Out-of-vocabulary check
                all_words = re.findall(r"\b[a-zA-Z]{3,}\b", cleaned_text.lower())
                has_any_kw = any(kw_matches.values())
                if top_conf < 0.28 and not has_any_kw:
                    return {
                        "category": "General",
                        "confidence": round(top_conf, 4),
                        "probabilities": prob_dict,
                        "method": "out_of_vocabulary_fallback",
                        "matching_keywords": [],
                        "explanation": "No distinctive academic vocabulary detected. Low confidence, classified as General.",
                    }

                # Ensure exact normalization before return
                total_p = sum(prob_dict.values())
                if total_p > 0:
                    prob_dict = {c: round(float(p / total_p), 4) for c, p in prob_dict.items()}
                top_conf = prob_dict[top_cat]

                matched_kws = kw_matches.get(top_cat, [])
                explanation = (
                    f"Classified as '{top_cat}' with {round(top_conf * 100, 1)}% confidence via TF-IDF + Logistic Regression."
                )
                if matched_kws:
                    explanation += f" Supporting signals: {', '.join(repr(w) for w in matched_kws[:4])}."

                return {
                    "category": top_cat,
                    "confidence": top_conf,
                    "probabilities": prob_dict,
                    "method": "machine_learning",
                    "matching_keywords": matched_kws,
                    "explanation": explanation,
                }
            except Exception:
                pass

        # Rule-Based Fallback if ML pipeline is unavailable
        if kw_matches:
            best_cat = max(kw_matches.keys(), key=lambda k: len(kw_matches[k]))
            hits = kw_matches[best_cat]
            conf = min(0.50 + len(hits) * 0.15, 0.95)
            prob_dict = {c: 0.05 for c in CATEGORIES}
            prob_dict[best_cat] = round(conf, 4)

            return {
                "category": best_cat,
                "confidence": round(conf, 4),
                "probabilities": prob_dict,
                "method": "rule_fallback",
                "matching_keywords": hits,
                "explanation": f"Classified as '{best_cat}' based on matched keywords: {', '.join(repr(w) for w in hits[:4])}.",
            }

        # Neutral fallback
        return {
            "category": "General",
            "confidence": 0.30,
            "probabilities": {c: round(1.0 / len(CATEGORIES), 3) for c in CATEGORIES},
            "method": "neutral_fallback",
            "matching_keywords": [],
            "explanation": "No strong category keywords identified. Assigned to General notice category.",
        }


# Global singleton instance for efficient inference
_classifier_instance: Optional[AnnouncementClassifier] = None


def classify_announcement(text: str) -> Dict[str, Any]:
    """Helper function to classify announcement text using global singleton classifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = AnnouncementClassifier()
    return _classifier_instance.predict(text)
