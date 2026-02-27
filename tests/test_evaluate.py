from fastapi.testclient import TestClient
from laf.api.main import app

client = TestClient(app)

def test_evaluate_no_pii_allowed():
    r = client.post("/evaluate", json={"input_text": "hello world", "data_classification": "INTERNAL"})
    assert r.status_code == 200
    data = r.json()
    assert data["allowed"] is True
    assert data["risk_score"] >= 0
    assert data["redactions_applied"] == []

def test_evaluate_pii_redaction():
    r = client.post("/evaluate", json={"input_text": "email me at test@example.com", "data_classification": "INTERNAL"})
    data = r.json()
    assert "EMAIL" in data["redactions_applied"]
    assert "[REDACTED:EMAIL]" in data["sanitized_text"]
    assert any(v["code"] == "PII_DETECTED" for v in data["violations"])

def test_restricted_blocks_pii():
    r = client.post("/evaluate", json={"input_text": "call 817-555-1212", "data_classification": "RESTRICTED"})
    data = r.json()
    assert data["allowed"] is False
    assert any(v["code"] == "RESTRICTED_PII_BLOCK" for v in data["violations"])
