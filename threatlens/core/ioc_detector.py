from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from core.normalizer import normalize_ioc

DOMAIN_REGEX = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$"
)
HEX_REGEX = re.compile(r"^[a-fA-F0-9]+$")


def detect_ioc_type(ioc: str) -> tuple[str, str]:
    normalized = normalize_ioc(ioc)
    lower = normalized.lower()

    if not normalized:
        return normalized, "unknown"

    if lower.startswith(("http://", "https://")):
        parsed = urlparse(normalized)
        if parsed.netloc:
            return normalized, "url"

    try:
        ipaddress.IPv4Address(normalized)
        return normalized, "ipv4"
    except ValueError:
        pass

    if DOMAIN_REGEX.match(normalized):
        return normalized.lower(), "domain"

    if HEX_REGEX.match(normalized):
        size = len(normalized)
        if size == 32:
            return normalized.lower(), "md5"
        if size == 40:
            return normalized.lower(), "sha1"
        if size == 64:
            return normalized.lower(), "sha256"

    return normalized, "unknown"
