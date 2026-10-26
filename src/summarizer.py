"""
SWYNEX Final AI Application - Intelligent Summarizer Module
Implements a local, lightweight, transparent extractive summarization algorithm.
Extracts the most salient sentences based on word frequency weighting,
positional importance, and action-verb relevance.
Guarantees ZERO hallucination because every output word originates verbatim from the input.
"""

import re
from typing import Dict, Any, List


# Comprehensive English stop words list for local processing without external downloads
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "should", "shouldn't", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "won't", "would", "wouldn't", "you", "your",
    "yours", "yourself", "yourselves"
}

# High-information action signals that indicate critical instructions
ACTION_SIGNALS = [
    "must", "submit", "deadline", "mandatory", "required", "scheduled",
    "announced", "closes", "due", "registered", "report", "strictly", "portal",
    "hall ticket", "admit card", "examination", "viva", "interviews"
]


def summarize_announcement(text: str, max_sentences: int = 2) -> Dict[str, Any]:
    """
    Generates a concise extractive summary of announcement text.

    Args:
        text: Announcement text.
        max_sentences: Maximum number of sentences to include in summary.

    Returns:
        Dictionary containing:
        - summary: Extracted concise summary string
        - original_chars: Character count of original text
        - summary_chars: Character count of summary text
        - compression_ratio: Percentage reduction
        - sentences_selected: Number of sentences in summary
        - method: Explanation of extractive scoring algorithm
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "summary": "No content provided to summarize.",
            "original_chars": 0,
            "summary_chars": 0,
            "compression_ratio": "0.0%",
            "sentences_selected": 0,
            "method": "Extractive frequency-based sentence ranking",
        }

    raw_text = text.strip()
    original_len = len(raw_text)

    # Split text into sentences using punctuation boundaries
    sentence_candidates = re.split(r"(?<=[.!?])\s+", raw_text)
    sentences = [s.strip() for s in sentence_candidates if s.strip()]

    # If already concise (1 or 2 sentences), return directly
    if len(sentences) <= max_sentences:
        return {
            "summary": raw_text,
            "original_chars": original_len,
            "summary_chars": original_len,
            "compression_ratio": "0.0% (Text already brief)",
            "sentences_selected": len(sentences),
            "method": "Verbatim pass-through (already concise)",
        }

    # Compute word frequency distribution
    words = re.findall(r"\b[a-zA-Z]{3,}\b", raw_text.lower())
    freq_table: Dict[str, int] = {}
    for word in words:
        if word not in STOP_WORDS:
            freq_table[word] = freq_table.get(word, 0) + 1

    max_freq = max(freq_table.values()) if freq_table else 1

    # Score each sentence
    sentence_scores: List[tuple] = []
    for idx, sentence in enumerate(sentences):
        score = 0.0
        s_words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())

        # Word frequency weight
        for w in s_words:
            if w in freq_table:
                score += freq_table[w] / max_freq

        # Lead sentence bias: first sentence frequently holds core notice subject
        if idx == 0:
            score *= 1.35

        # Action signal bonus: sentences with critical instructions
        s_lower = sentence.lower()
        for signal in ACTION_SIGNALS:
            if signal in s_lower:
                score += 1.5

        sentence_scores.append((idx, score, sentence))

    # Rank sentences by score descending, pick top N, then sort by original order
    sentence_scores.sort(key=lambda item: item[1], reverse=True)
    top_sentences = sentence_scores[:max_sentences]
    top_sentences.sort(key=lambda item: item[0])

    summary_text = " ".join(item[2] for item in top_sentences)
    summary_len = len(summary_text)

    reduction = ((original_len - summary_len) / original_len) * 100 if original_len > 0 else 0.0
    compression_str = f"{round(max(reduction, 0.0), 1)}% reduction"

    return {
        "summary": summary_text,
        "original_chars": original_len,
        "summary_chars": summary_len,
        "compression_ratio": compression_str,
        "sentences_selected": len(top_sentences),
        "method": "Transparent Extractive Sentence Ranking (Zero Hallucination)",
    }
