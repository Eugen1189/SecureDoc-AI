from src.utils.pii_masker import mask_pii

def test_mask_email():
    text = "Contact me at test@example.com for more info."
    masked = mask_pii(text)
    assert "[EMAIL_MASKED]" in masked
    assert "test@example.com" not in masked

def test_mask_phone():
    text = "My phone is +49 123 456 7890."
    masked = mask_pii(text)
    assert "[PHONE_MASKED]" in masked
    assert "+49 123 456 7890" not in masked

def test_mask_iban():
    text = "The IBAN is DE89370400440532013000."
    masked = mask_pii(text)
    assert "[IBAN_MASKED]" in masked
    assert "DE89370400440532013000" not in masked

def test_no_pii():
    text = "Hello world!"
    masked = mask_pii(text)
    assert masked == "Hello world!"
