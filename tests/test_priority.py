"""
SWYNEX Final AI Application - Test Suite: Priority Detection Module
Tests priority scoring, urgency markers, penalty penalties, and routine mitigations.
"""

import pytest
from src.priority_detector import detect_priority


class TestPriorityDetector:
    """Tests priority scoring and explainable reason generation."""

    def test_high_priority_imminent_deadline(self):
        text = "URGENT: Submit exam registration with late fee strictly tonight before 11:59 PM or face debarment."
        res = detect_priority(text, category="Exam", has_detected_deadline=True)
        assert res["priority"] == "High"
        assert res["score"] >= 60
        assert len(res["urgency_factors"]) > 0
        assert "debarment" in res["urgency_factors"][0] or "Critical" in res["urgency_factors"][0]

    def test_medium_priority_upcoming_event(self):
        text = "Annual Inter-College Hackathon registration closes on November 5. Register with your team."
        res = detect_priority(text, category="Event", has_detected_deadline=True)
        assert res["priority"] in ["Medium", "High"]
        assert 35 <= res["score"] <= 85

    def test_low_priority_informational_notice(self):
        text = "General notice: The campus library will observe normal hours. Biometric attendance records updated."
        res = detect_priority(text, category="General", has_detected_deadline=False)
        assert res["priority"] == "Low"
        assert res["score"] < 45

    def test_urgent_care_false_alarm_mitigation(self):
        # 'urgent care' clinic should NOT trigger High priority for a health clinic notice
        text = "The urgent care first-aid health clinic is located on ground floor. Open 9 AM to 5 PM."
        res = detect_priority(text, category="General", has_detected_deadline=False)
        assert res["priority"] == "Low"

    def test_emergency_weather_closure_high_priority(self):
        text = "Emergency closure: Severe cyclone alert issued. Campus will be evacuated today by 2:00 PM."
        res = detect_priority(text, category="Holiday", has_detected_deadline=True)
        assert res["priority"] == "High"
        assert res["score"] >= 65
