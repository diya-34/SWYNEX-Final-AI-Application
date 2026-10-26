"""
SWYNEX Final AI Application - Test Suite: Information Extractor Module
Tests date extraction, deadline classification, URLs, emails, action tags,
and transparent missing-date notifications.
"""

import pytest
from src.information_extractor import extract_information


class TestInformationExtractor:
    """Tests date, deadline, entity, and contact extraction."""

    def test_explicit_date_and_time_extraction(self):
        text = "Practical lab examinations will commence from Monday, November 10 at 9:00 AM in Lab 4."
        res = extract_information(text)
        assert res["has_date"] is True
        assert len(res["dates"]) > 0
        assert "9:00 AM" in res["times"] or "9:00 am" in [t.lower() for t in res["times"]]

    def test_deadline_detection(self):
        text = "Final submission deadline is October 25, 2026. Submit before Friday 5:00 PM."
        res = extract_information(text)
        assert res["has_deadline"] is True
        assert len(res["deadlines"]) > 0

    def test_url_and_email_extraction(self):
        text = "Download admit cards at https://exam.university.edu or contact coe@university.edu for queries."
        res = extract_information(text)
        assert len(res["urls"]) > 0
        assert "https://exam.university.edu" in res["urls"]
        assert len(res["emails"]) > 0
        assert "coe@university.edu" in res["emails"]

    def test_action_keywords_extraction(self):
        text = "Students must bring their Hall Ticket and Admit Card. Late Fine applies after due date."
        res = extract_information(text)
        assert "Hall Ticket" in res["keywords"] or "Admit Card" in res["keywords"]

    def test_missing_date_notification(self):
        text = "The campus Wi-Fi network will undergo routine maintenance. Thank you for your patience."
        res = extract_information(text)
        assert res["has_date"] is False
        assert res["has_deadline"] is False
        assert "No explicit date detected" in res["status_messages"]["dates"]
