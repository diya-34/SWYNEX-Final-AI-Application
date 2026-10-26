"""
SWYNEX Final AI Application - Test Suite: Classification Module
Verifies category predictions, calibrated probabilities, cold-start fallback,
and out-of-vocabulary handling.
"""

import pytest
from src.classifier import classify_announcement, CATEGORIES, AnnouncementClassifier


class TestAnnouncementClassifier:
    """Tests the hybrid classification module."""

    @pytest.fixture(scope="class")
    @classmethod
    def classifier(cls):
        return AnnouncementClassifier()

    def test_supported_categories_count(self):
        assert len(CATEGORIES) == 7
        for cat in ["Exam", "Assignment", "Event", "Placement", "Internship", "Holiday", "General"]:
            assert cat in CATEGORIES

    @pytest.mark.parametrize("text,expected_category", [
        ("The End-Semester Examination timetable has been released. Admit cards available.", "Exam"),
        ("Submit your Machine Learning Assignment 2 before Friday 11:59 PM on Canvas LMS.", "Assignment"),
        ("Join us for HackSphere 2026, the 24-hour national hackathon in the main auditorium.", "Event"),
        ("Microsoft campus placement drive: Shortlisted candidates technical interviews tomorrow.", "Placement"),
        ("6-month winter internship opportunity with Rs 25,000 monthly stipend at research lab.", "Internship"),
        ("The college will remain closed on Monday for Dussehra holiday. Classes resume Tuesday.", "Holiday"),
        ("Notice: Smart biometric ID cards ready for collection at administrative counter 4.", "General"),
    ])
    def test_category_predictions(self, classifier, text, expected_category):
        res = classifier.predict(text)
        assert res["category"] == expected_category
        assert 0.0 <= res["confidence"] <= 1.0
        assert isinstance(res["probabilities"], dict)
        assert len(res["probabilities"]) == 7

    def test_probabilities_sum_to_one(self, classifier):
        text = "Mid-term examination schedule for Computer Science department."
        res = classifier.predict(text)
        prob_sum = sum(res["probabilities"].values())
        assert pytest.approx(prob_sum, abs=0.05) == 1.0

    def test_gibberish_out_of_vocabulary_fallback(self, classifier):
        gibberish = "xyzabc qwerty123987 nonexistingwordzzzz"
        res = classifier.predict(gibberish)
        assert res["category"] == "General"
        assert res["confidence"] <= 0.40
