"""
SWYNEX Final AI Application - Input Validation & Sanitization Module
Provides input validation, empty-input handling, whitespace stripping,
maximum character length enforcement, and safe error fallbacks.
"""

from typing import Tuple, Optional


MAX_INPUT_CHARS = 4000
MIN_MEANINGFUL_CHARS = 3


def validate_input(
    text: any,
    max_chars: int = MAX_INPUT_CHARS,
    min_chars: int = MIN_MEANINGFUL_CHARS
) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    Validates and sanitizes raw user input.

    Args:
        text: Input text from user or API caller.
        max_chars: Maximum allowable character count before safe truncation.
        min_chars: Minimum character length required for meaningful analysis.

    Returns:
        Tuple of (is_valid, cleaned_text, error_message, warning_message)
    """
    # 1. Null / None check
    if text is None:
        return (
            False,
            "",
            "Input text cannot be None. Please provide a valid text string.",
            None
        )

    # 2. Type validation
    if not isinstance(text, str):
        return (
            False,
            "",
            f"Expected string input, but received {type(text).__name__}.",
            None
        )

    # 3. Clean and strip whitespace
    cleaned = text.strip()

    # 4. Empty or whitespace-only check
    if not cleaned:
        return (
            False,
            "",
            "Input announcement is empty or contains only whitespace. Please enter announcement text.",
            None
        )

    # 5. Too short / insufficient content check
    if len(cleaned) < min_chars:
        return (
            False,
            cleaned,
            f"Input is too brief ({len(cleaned)} characters). Minimum {min_chars} characters required.",
            None
        )

    # 6. Length safety check and truncation warning
    warning = None
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
        warning = (
            f"Input exceeded maximum safe limit of {max_chars} characters. "
            f"Safely truncated to first {max_chars} characters for analysis."
        )

    return True, cleaned, None, warning
