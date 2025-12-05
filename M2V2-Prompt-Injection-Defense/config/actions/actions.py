import re
from typing import Optional


def prompt_injection_check(user_message: str):
    """Legacy function - kept for compatibility."""
    lowered = user_message.lower()
    attack_phrases = [
        "ignore previous instructions",
        "ignore all instructions",
        "forget all prior instructions",
        "pls ignore",
        "developer mode",
        "dan",
        "jailbreak",
        "do anything now",
        "system prompt",
        "last 10 user queries",
    ]
    return "ATTACK" if any(p in lowered for p in attack_phrases) else "SAFE"


def check_pii_in_text(text: str) -> bool:
    """
    Check if text contains potential PII like emails.
    Uses regex to detect actual email patterns, not just @ and . symbols.
    """
    # Email pattern: requires alphanumeric before @, domain, and TLD
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    # Check if there's an actual email match
    matches = re.findall(email_pattern, text)

    # Return True only if we found actual email addresses
    return len(matches) > 0
