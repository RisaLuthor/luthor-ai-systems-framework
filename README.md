![CI](https://github.com/YOUR-USERNAME/luthor-ai-systems-framework/actions/workflows/ci.yml/badge.svg)

# luthor-ai-systems-framework

Deterministic AI governance and safety framework designed for enterprise LLM deployment, policy enforcement, sensitive data control, and audit traceability.

---

## Overview

The Luthor AI Systems Framework is a modular governance layer for enterprise AI systems. It evaluates model input against structured policy profiles, detects and redacts sensitive data (PII), applies classification-aware enforcement rules, computes normalized risk scores, and produces structured audit trails suitable for compliance and observability systems.

The framework is deterministic by design — no stochastic behavior in policy enforcement — making it suitable for regulated environments, internal AI deployments, and controlled LLM integration pipelines.

---

## Core Capabilities

- Deterministic policy evaluation engine  
- PII detection and structured redaction (`[REDACTED:EMAIL]`, `[REDACTED:PHONE]`)  
- Classification-aware enforcement (INTERNAL vs RESTRICTED)  
- Risk scoring (0–100 scale)  
- Structured violation contracts  
- Audit trail persistence (SQLite)  
- REST API (FastAPI)  
- CLI interface  
- Full pytest coverage  

---

## Architecture

The framework is structured into modular components:

laf/
├── api/ # FastAPI application + routes
├── governance/ # Policy engine, models, PII detection
├── storage/ # Audit persistence layer
└── cli/ # Command-line interface


Request Flow:

1. Client submits input for evaluation
2. Policy engine evaluates content deterministically
3. PII detection and redaction applied
4. Risk score computed
5. Violations structured
6. Audit record persisted
7. Structured response returned

---

## Example API Usage

### Request

```bash
POST /evaluate
```

```
{
  "input_text": "email me at test@example.com",
  "data_classification": "INTERNAL"
}
```

## Response

```
{
  "allowed": true,
  "risk_score": 35,
  "violations": [
    {
      "code": "FINDINGS_DETECTED",
      "message": "Sensitive data detected in input."
    }
  ],
  "redactions_applied": ["EMAIL"],
  "sanitized_text": "email me at [REDACTED:EMAIL]",
  "audit_trail": [
    "Policy profile: default",
    "PII detected: EMAIL",
    "Risk score calculated"
  ]
}
```

## Deterministic Governance Philosophy

Enterprise AI governance must be:

Repeatable
Explainable
Auditable
Classification-aware
This framework avoids probabilistic filtering in enforcement logic.
Every decision is traceable and reproducible.

## Running Locally

Install Dependencies

```
pip install -r requirements.txt
```

## Run API

```
uvicorn laf.api.main:app --reload
```

## Run Tests

```
pytest -q
```

## Docker

Build:

```
docker build -t luthor-ai-systems-framework .
```

Run:

```
docker run -p 8000:8000 luthor-ai-systems-framework
```

## Use Cases

Enterprise LLM gateway governance layer
Pre-processing middleware for AI services
Internal compliance enforcement
Secure AI experimentation environments
AI innovation sandbox with guardrails

## License

MIT License


---

Now your repo looks:

• Clean  
• Enterprise  
• Intentional  
• Architect-level  

---

Next move:

Do we add:

1️⃣ A security considerations section  
2️⃣ CI badge + coverage badge  
3️⃣ Release notes section  
4️⃣ Architecture diagram image (for visual impact)  

Choose deliberately.

## Releases

### v1.0.0
- Deterministic policy engine
- PII detection and redaction
- Classification-aware enforcement
- Risk scoring (0–100)
- Structured violations
- SQLite audit logging
- REST + CLI interfaces
- Full test coverage


## Releases
- v0.2.0 — Scenario-driven governance simulation engine (CLI + reports)
