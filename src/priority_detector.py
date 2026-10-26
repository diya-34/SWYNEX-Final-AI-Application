"""
SWYNEX Final AI Application - Priority Detection Module
Analyzes urgency, time sensitivity, deadlines, penalties, and key action terms
to assign High, Medium, or Low priority with an auditable, transparent reason.
"""

import re
from typing import Dict, Any, List, Optional


# Keywords signaling immediate or critical urgency (supports singular & plural)
HIGH_URGENCY_KEYWORDS = [
    r"urgent(?! care)", r"urgently", r"immediately", r"immediate", r"strictly tonight",
    r"today", r"tonight", r"tomorrow", r"within 24 hours", r"within 48 hours",
    r"last date", r"final call", r"last chance", r"without fail", r"strictly compulsory",
    r"compulsory", r"mandatory", r"hall tickets?", r"admit cards?",
    r"debarment", r"debarred", r"late fines?", r"late fees?", r"zero marks",
    r"penalt(y|ies)", r"strict compliance", r"evacuated", r"emergency closure",
    r"cyclone alert", r"severe", r"shortlisted candidates?", r"before friday"
]

# Keywords signaling moderate urgency / standard deadlines
MEDIUM_URGENCY_KEYWORDS = [
    r"deadline", r"due date", r"submit before", r"registration forms?", r"apply before",
    r"upcoming", r"schedule", r"commence", r"closes on", r"viva voce",
    r"mid-semester", r"backlog", r"re-evaluation", r"interviews?", r"assessments?",
    r"hackathon", r"workshop", r"fees?", r"dues?", r"prior notice", r"within a week",
    r"stipend of", r"training session", r"mock interview", r"closed on monday"
]

# Keywords signaling low urgency / informational notices
LOW_URGENCY_KEYWORDS = [
    r"for your information", r"fyi", r"optional", r"general notice", r"library hours",
    r"biometric", r"smart cards?", r"wi-fi maintenance", r"lost and found",
    r"canteen", r"bus concession", r"theme announced", r"winter break",
    r"annual sports", r"guest lecture", r"auditions?", r"urgent care",
    r"in due course", r"check back soon", r"elective courses", r"health checkup",
    r"gymnasium", r"inspection"
]


def detect_priority(
    text: str,
    category: str = "General",
    has_detected_deadline: bool = False
) -> Dict[str, Any]:
    """
    Evaluates urgency and assigns a priority level (High, Medium, Low)
    along with an auditable explanation.

    Args:
        text: Raw announcement text.
        category: Classified category (e.g. Exam, Assignment).
        has_detected_deadline: Boolean indicating whether deadline patterns were found.

    Returns:
        Dictionary with priority ('High', 'Medium', 'Low'), score (0-100),
        reason, urgency_factors, and recommended action.
    """
    if not text or not text.strip():
        return {
            "priority": "Low",
            "score": 0,
            "reason": "Announcement text is empty; defaulted to Low priority.",
            "urgency_factors": [],
            "recommended_action": "Provide announcement text to analyze priority."
        }

    text_lower = text.lower()
    score = 25  # Baseline neutral score
    factors: List[str] = []

    # 1. Check High Urgency Keywords
    matched_high = []
    for pattern in HIGH_URGENCY_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", text_lower):
            matched_high.append(pattern.replace(r"\b", "").replace("?", ""))

    if matched_high:
        score += min(len(matched_high) * 20, 50)
        clean_terms = [re.sub(r"[(\|)s]", "", w) for w in matched_high[:3]]
        factors.append(f"Critical urgency terms: {', '.join(repr(w) for w in clean_terms)}")

    # 2. Check Medium Urgency Keywords
    matched_medium = []
    for pattern in MEDIUM_URGENCY_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", text_lower):
            matched_medium.append(pattern.replace(r"\b", "").replace("?", ""))

    if matched_medium:
        score += min(len(matched_medium) * 10, 25)
        clean_terms = [re.sub(r"[(\|)s]", "", w) for w in matched_medium[:3]]
        factors.append(f"Action/deadline indicators: {', '.join(repr(w) for w in clean_terms)}")

    # 3. Check Low Urgency Signals (Mitigation)
    matched_low = []
    for pattern in LOW_URGENCY_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", text_lower):
            matched_low.append(pattern.replace(r"\b", ""))

    if matched_low and not matched_high:
        score = max(score - 15, 10)
        clean_terms = [re.sub(r"[(\|)s]", "", w) for w in matched_low[:2]]
        factors.append(f"Informational/routine signals: {', '.join(repr(w) for w in clean_terms)}")

    # 4. Contextual Category Weighting
    if category in ["Exam", "Placement"]:
        if matched_high or has_detected_deadline:
            score += 15
            factors.append(f"High-stakes category '{category}' with imminent deadline.")
        else:
            score += 5
    elif category == "Assignment":
        if has_detected_deadline or matched_high:
            score += 15
            factors.append("Academic coursework submission with active deadline.")
    elif category == "Holiday":
        if "cyclone" in text_lower or "emergency" in text_lower or "evacuated" in text_lower:
            score += 35
            factors.append("Emergency campus closure alert.")

    # 5. Cap and Map Score to Priority Level
    final_score = int(np_clip(score, 0, 100))

    if final_score >= 60:
        priority = "High"
        recommended_action = "Take immediate action today. Verify deadlines, admit cards, or submissions immediately."
        reason = f"High priority (Score: {final_score}/100) due to time-sensitive keywords and strict compliance."
    elif final_score >= 35:
        priority = "Medium"
        recommended_action = "Schedule this task in your calendar. Ensure required deliverables are completed on time."
        reason = f"Medium priority (Score: {final_score}/100) due to upcoming scheduled dates or registration requirements."
    else:
        priority = "Low"
        recommended_action = "Informational notice for your awareness. No immediate action required."
        reason = f"Low priority (Score: {final_score}/100); routine administrative or general informational notice."

    return {
        "priority": priority,
        "score": final_score,
        "reason": reason,
        "urgency_factors": factors,
        "recommended_action": recommended_action
    }


def np_clip(val: float, min_val: float, max_val: float) -> float:
    """Safe fallback clipping without hard dependency on numpy."""
    return max(min_val, min(val, max_val))
