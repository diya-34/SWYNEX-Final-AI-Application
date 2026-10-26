"""
SWYNEX Final AI Application - Test Suite: Summarizer Module
Tests extractive summarization, zero-hallucination property, compression metrics,
and length thresholds.
"""

import pytest
from src.summarizer import summarize_announcement


class TestSummarizer:
    """Tests the extractive zero-hallucination summarizer."""

    def test_short_text_verbatim_passthrough(self):
        text = "Mid-term examinations will begin on Monday."
        res = summarize_announcement(text, max_sentences=2)
        assert res["summary"] == text
        assert res["sentences_selected"] == 1

    def test_multi_sentence_extractive_summary(self):
        text = (
            "The Department of Computer Science has announced the End-Semester Examination timetable. "
            "All students must download their admit cards before Friday 5:00 PM from the exam portal. "
            "Failure to present the printed admit card will lead to debarment from the examination hall. "
            "Please reach out to the examination superintendent in Room 102 for seating queries."
        )
        res = summarize_announcement(text, max_sentences=2)
        assert len(res["summary"]) < len(text)
        assert res["sentences_selected"] == 2
        # Zero-hallucination verification: each word of summary must exist in original text
        summary_sentences = [s.strip() for s in res["summary"].split(".") if s.strip()]
        for s in summary_sentences:
            assert s in text

    def test_compression_ratio_calculation(self):
        text = (
            "Sentence one describes the general situation. "
            "Sentence two explains the core requirement that must be submitted immediately. "
            "Sentence three provides secondary logistics details. "
            "Sentence four mentions additional optional contacts."
        )
        res = summarize_announcement(text, max_sentences=2)
        assert res["original_chars"] > res["summary_chars"]
        assert "%" in res["compression_ratio"]

    def test_empty_text_summarization(self):
        res = summarize_announcement("")
        assert res["summary"] == "No content provided to summarize."
        assert res["sentences_selected"] == 0
