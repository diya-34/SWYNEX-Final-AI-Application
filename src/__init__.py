"""
SWYNEX Final AI Application - Student Announcement Intelligence System
Package initialization and unified end-to-end processing pipeline.
"""

import time
from typing import Dict, Any

from src.validator import validate_input, MAX_INPUT_CHARS, MIN_MEANINGFUL_CHARS
from src.classifier import classify_announcement, AnnouncementClassifier, CATEGORIES
from src.priority_detector import detect_priority
from src.information_extractor import extract_information
from src.summarizer import summarize_announcement


__version__ = "1.0.0"
__author__ = "SWYNEX AI Internship - Task 4"


def analyze_announcement(raw_text: str) -> Dict[str, Any]:
    """
    Executes the complete end-to-end intelligence pipeline on announcement text.

    Pipeline steps:
    1. Input validation & sanitization (handling null, empty, whitespace, length)
    2. Category classification (TF-IDF + Logistic Regression + Keyword fallback)
    3. Information extraction (dates, deadlines, times, URLs, emails, action tags)
    4. Urgency & Priority detection (High/Medium/Low with scoring and explainability)
    5. Extractive summarization (salient sentences, zero hallucination)

    Returns:
        Structured dictionary containing all analysis components and execution metadata.
    """
    start_time = time.perf_counter()

    # 1. Validation
    is_valid, cleaned_text, error_msg, warning_msg = validate_input(raw_text)

    if not is_valid:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error": error_msg,
            "warning": warning_msg,
            "execution_time_ms": elapsed,
            "raw_text": raw_text,
            "classification": {
                "category": "General",
                "confidence": 0.0,
                "probabilities": {c: 0.0 for c in CATEGORIES},
                "method": "validation_failure_fallback",
                "explanation": error_msg,
            },
            "priority": {
                "priority": "Low",
                "score": 0,
                "reason": error_msg,
                "urgency_factors": [],
                "recommended_action": "Enter valid announcement text.",
            },
            "extraction": {
                "dates": [],
                "deadlines": [],
                "times": [],
                "urls": [],
                "emails": [],
                "keywords": [],
                "has_date": False,
                "has_deadline": False,
                "status_messages": {
                    "dates": "No dates found.",
                    "deadlines": "No deadlines found.",
                    "urls": "No URLs found.",
                    "emails": "No email addresses found.",
                    "keywords": "No keywords found.",
                },
            },
            "summary": {
                "summary": "No content provided to summarize.",
                "original_chars": 0,
                "summary_chars": 0,
                "compression_ratio": "0.0%",
                "sentences_selected": 0,
                "method": "None",
            },
        }

    # 2. Classification
    classification_res = classify_announcement(cleaned_text)

    # 3. Information Extraction
    extraction_res = extract_information(cleaned_text)

    # 4. Priority Detection
    priority_res = detect_priority(
        cleaned_text,
        category=classification_res["category"],
        has_detected_deadline=extraction_res["has_deadline"]
    )

    # 5. Summarization
    summary_res = summarize_announcement(cleaned_text)

    elapsed = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "success": True,
        "error": None,
        "warning": warning_msg,
        "execution_time_ms": elapsed,
        "cleaned_text": cleaned_text,
        "classification": classification_res,
        "priority": priority_res,
        "extraction": extraction_res,
        "summary": summary_res,
    }
