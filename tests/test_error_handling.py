"""
SWYNEX Final AI Application - Test Suite: Error Handling & Edge Cases
Tests empty inputs, whitespace, None, invalid types, oversized text,
gibberish strings, and unified analyze_announcement pipeline resilience.
"""

import pytest
from src.validator import validate_input
from src import analyze_announcement


class TestErrorHandlingAndValidation:
    """Tests rigorous edge-case and error handling."""

    def test_empty_string_input(self):
        is_valid, cleaned, err, warn = validate_input("")
        assert is_valid is False
        assert "empty or contains only whitespace" in err

        res = analyze_announcement("")
        assert res["success"] is False
        assert res["error"] is not None
        assert res["classification"]["category"] == "General"
        assert res["priority"]["priority"] == "Low"

    def test_whitespace_only_input(self):
        is_valid, cleaned, err, warn = validate_input("   \n\t   ")
        assert is_valid is False
        assert err is not None

        res = analyze_announcement("   \t\n  ")
        assert res["success"] is False

    def test_none_input(self):
        is_valid, cleaned, err, warn = validate_input(None)
        assert is_valid is False
        assert "cannot be None" in err

        res = analyze_announcement(None)
        assert res["success"] is False
        assert "cannot be None" in res["error"]

    def test_non_string_types(self):
        is_valid, cleaned, err, warn = validate_input(12345)
        assert is_valid is False
        assert "Expected string" in err

        is_valid, cleaned, err, warn = validate_input(["announcement"])
        assert is_valid is False

    def test_unusually_long_text_safety(self):
        # 10,000 character synthetic text
        massive_text = "Important university circular. " * 350
        is_valid, cleaned, err, warn = validate_input(massive_text, max_chars=4000)
        assert is_valid is True
        assert len(cleaned) == 4000
        assert warn is not None
        assert "Safely truncated" in warn

        # Verify pipeline handles safely without crash
        res = analyze_announcement(massive_text)
        assert res["success"] is True
        assert res["warning"] is not None
        assert "category" in res["classification"]

    def test_gibberish_input_safe_handling(self):
        gibberish = "asdkjhf 12837198273 zxmncbv qwpoeiruy"
        res = analyze_announcement(gibberish)
        assert res["success"] is True
        assert res["classification"]["category"] == "General"
        assert res["extraction"]["has_date"] is False
        assert res["priority"]["priority"] == "Low"
