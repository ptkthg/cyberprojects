from __future__ import annotations


def normalize_ioc(ioc: str) -> str:
    """Sanitize IOC input and normalize common obfuscations."""
    value = (ioc or "").strip()
    value = value.replace("[.]", ".").replace("hxxp://", "http://").replace("hxxps://", "https://")
    return " ".join(value.split())
