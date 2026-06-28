# MedGuard AI Pipeline Starter

The backend can call this folder through the local AI adapter.

Current local module:

```text
medguard_ai_pipeline.py
```

Required function:

```python
def answer_question(question: str, snapshot: dict) -> dict:
    ...
```

The backend sends a snapshot with:

- user profile
- medications
- supplements
- substances and lifestyle factors
- current rule-based safety result

Return a dictionary with:

- `answer`
- `recommendation`
- optional `related_interactions`
- `disclaimer`

This starter is intentionally rule-based and medically cautious. It does not call a real LLM yet.
