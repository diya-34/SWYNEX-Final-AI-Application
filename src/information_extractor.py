"""
SWYNEX Final AI Application - Important Information Extraction Module
Uses regular expressions and rule-based heuristics to extract:
- Explicit dates and times
- Deadlines vs general scheduled dates
- Relative temporal indicators (e.g. tomorrow, tonight, next Monday)
- URLs and website portals
- Contact email addresses
- Action keywords and entity tags
Provides clear fallback notices when information is not found.
"""

import re
from typing import Dict, Any, List, Optional


# Regular expressions for dates and temporal expressions
DATE_PATTERNS = [
    # Full Month Day, Year (e.g. October 25, 2026 / Oct 25, 2026 / 25th October 2026)
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\b",
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:,?\s+\d{4})?\b",
    # DD/MM/YYYY or DD-MM-YYYY
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    # Day with date range (e.g. December 2 to December 5)
    r"\b(?:December|November|October|September|August|July|June|May|April|March|February|January)\s+\d{1,2}\s+to\s+(?:December|November|October|September|August|July|June|May|April|March|February|January)?\s*\d{1,2}\b",
    # Day with time (e.g. Monday, November 10 at 9:00 AM / Friday 5:00 PM / Wednesday before 4 PM)
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:,?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2})?(?:\s+(?:at|before|from|by)\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))?\b",
]

# Time patterns (e.g. 11:59 PM, 5:00 PM, 9:00 AM, 12:00 PM)
TIME_PATTERN = r"\b\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)\b"

# Relative temporal indicators
RELATIVE_DATES = [
    "strictly tonight", "tonight", "tomorrow morning", "tomorrow afternoon",
    "tomorrow", "today", "next monday", "next wednesday", "next tuesday",
    "next week", "this friday", "this saturday", "this thursday", "this wednesday",
    "within 24 hours", "within 48 hours", "in due course"
]

# Patterns explicitly signaling a cutoff deadline
DEADLINE_PREFIX_PATTERNS = [
    r"(?:before|by|due|until|closes strictly|deadline is|close strictly|due tomorrow by|submit before|register before|closes on)\s+([A-Za-z0-9,:\s\-\/]+?)(?=[.,;]|$)",
    r"(?:strictly tonight\s+at\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)",
    r"(?:tomorrow\s+by\s+\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)",
]

# URL pattern supporting http, https, www, and common academic/dev domain paths
URL_PATTERN = r"\b(?:https?://[^\s<>\"']+|www\.[^\s<>\"']+|[a-zA-Z0-9.-]+\.(?:edu|ac\.in|org|com|dev|io|gov\.in)(?:/[^\s<>\"']*)?)\b"

# Standard email pattern
EMAIL_PATTERN = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

# Domain-specific action tags & keyword entities
ACTION_TAG_KEYWORDS = [
    "Admit Card", "Hall Ticket", "Seating Arrangement", "Late Fine", "Late Fee",
    "Turnitin", "Google Classroom", "Canvas LMS", "ERP Portal", "GitHub Repository",
    "Viva Voce", "Capstone Project", "Aptitude Test", "Technical Interview",
    "Mock Interview", "Resume Submission", "Bonafide Certificate", "Smart ID Card",
    "Scholarship", "Weather Advisory", "Biometric", "Debarment"
]


def extract_information(text: str) -> Dict[str, Any]:
    """
    Extracts structured entities from announcement text.

    Returns:
        Dictionary containing:
        - dates: list of identified date strings
        - deadlines: list of high-priority deadline strings
        - times: list of extracted time strings
        - urls: list of valid URLs
        - emails: list of valid email addresses
        - keywords: list of action tags detected
        - has_date: boolean flag whether any date was detected
        - has_deadline: boolean flag whether any deadline was detected
        - status_messages: user-friendly status messages for missing items
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "dates": [],
            "deadlines": [],
            "times": [],
            "urls": [],
            "emails": [],
            "keywords": [],
            "has_date": False,
            "has_deadline": False,
            "status_messages": {
                "dates": "No dates found (empty input).",
                "deadlines": "No deadlines found (empty input).",
                "urls": "No URLs found (empty input).",
                "emails": "No email addresses found (empty input).",
                "keywords": "No action keywords found (empty input).",
            }
        }

    raw_text = text.strip()
    text_lower = raw_text.lower()

    # 1. Extract Dates
    found_dates = []
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, raw_text, flags=re.IGNORECASE)
        for m in matches:
            clean_m = m.strip(" ,.")
            if clean_m and clean_m not in found_dates:
                found_dates.append(clean_m)

    # 2. Extract Relative Dates
    for rel in RELATIVE_DATES:
        if re.search(r"\b" + re.escape(rel) + r"\b", text_lower):
            title_rel = rel.title()
            if title_rel not in found_dates:
                found_dates.append(title_rel)

    # 3. Extract Times
    found_times = []
    for m in re.finditer(TIME_PATTERN, raw_text, flags=re.IGNORECASE):
        t_str = m.group(0).strip(" ,.")
        if t_str not in found_times:
            found_times.append(t_str)

    # 4. Extract Deadlines (Time-sensitive action deadlines)
    found_deadlines = []
    for d_pat in DEADLINE_PREFIX_PATTERNS:
        matches = re.finditer(d_pat, raw_text, flags=re.IGNORECASE)
        for m in matches:
            deadline_str = m.group(0).strip(" ,.;")
            if deadline_str and deadline_str not in found_deadlines:
                found_deadlines.append(deadline_str)

    # If relative urgency terms like 'strictly tonight' or 'tomorrow' exist with due verbs, add them
    if ("strictly tonight" in text_lower or "tonight at" in text_lower) and not found_deadlines:
        found_deadlines.append("Strictly Tonight")
    elif "due tomorrow" in text_lower and not found_deadlines:
        found_deadlines.append("Due Tomorrow")

    # 5. Extract URLs
    found_urls = []
    for m in re.finditer(URL_PATTERN, raw_text, flags=re.IGNORECASE):
        u = m.group(0).strip(" .,;()")
        if u not in found_urls and ("." in u):
            found_urls.append(u)

    # 6. Extract Emails
    found_emails = []
    for m in re.finditer(EMAIL_PATTERN, raw_text):
        e = m.group(0).strip(" .,;")
        if e not in found_emails:
            found_emails.append(e)

    # 7. Extract Action Tags
    found_keywords = []
    for tag in ACTION_TAG_KEYWORDS:
        if re.search(r"\b" + re.escape(tag) + r"\b", raw_text, flags=re.IGNORECASE):
            if tag not in found_keywords:
                found_keywords.append(tag)

    has_date = len(found_dates) > 0
    has_deadline = len(found_deadlines) > 0

    # User-friendly status messages explaining missing elements
    status_messages = {
        "dates": (
            f"Detected {len(found_dates)} date reference(s)."
            if has_date else
            "⚠️ No explicit date detected. Please check official notice boards or the ERP portal."
        ),
        "deadlines": (
            f"Detected {len(found_deadlines)} critical deadline(s)."
            if has_deadline else
            "No specific deadline detected in this announcement text."
        ),
        "urls": (
            f"Detected {len(found_urls)} link(s)."
            if found_urls else
            "No web links or portal URLs detected."
        ),
        "emails": (
            f"Detected {len(found_emails)} contact email(s)."
            if found_emails else
            "No official contact email addresses detected."
        ),
        "keywords": (
            f"Found {len(found_keywords)} action entity tag(s)."
            if found_keywords else
            "No high-priority action tags detected."
        ),
    }

    return {
        "dates": found_dates,
        "deadlines": found_deadlines,
        "times": found_times,
        "urls": found_urls,
        "emails": found_emails,
        "keywords": found_keywords,
        "has_date": has_date,
        "has_deadline": has_deadline,
        "status_messages": status_messages,
    }
