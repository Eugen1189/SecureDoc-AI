import re
import structlog

logger = structlog.get_logger()

# Regex patterns for PII
EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
# Simplified EU phone pattern (covers common formats with + prefix or 00)
PHONE_PATTERN = r"(?:\+|00)[1-9][0-9 \-\(\)\.]{7,32}"
# IBAN pattern (General format: 2 letters + 2 digits + up to 30 alphanumeric)
IBAN_PATTERN = r"[A-Z]{2}[0-9]{2}[A-Z0-9]{4,30}"

PII_PATTERNS = {
    "EMAIL": EMAIL_PATTERN,
    "PHONE": PHONE_PATTERN,
    "IBAN": IBAN_PATTERN
}

def mask_pii(text: str) -> str:
    """
    Masks Emails, Phone Numbers (EU), and IBANs in the provided text.
    Uses regex and logs masking actions via structlog.
    """
    masked_text = text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, masked_text)
        if matches:
            logger.info("pii_detected", type=pii_type, count=len(matches))
            masked_text = re.sub(pattern, f"[{pii_type}_MASKED]", masked_text)
            
    return masked_text
