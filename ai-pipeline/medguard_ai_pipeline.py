from __future__ import annotations

from typing import Any

DISCLAIMER = "This is not medical advice. Consult a doctor or pharmacist."


def answer_question(question: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Starter local AI module.

    The backend calls this function from /assistant/ask. Replace this function
    with the real AI team's model or retrieval logic when it is ready.
    """
    question_lower = question.lower()
    safety = snapshot.get("rule_based_safety_result", {})
    interactions = safety.get("interactions", [])

    if interactions:
        relevant = [
            item
            for item in interactions
            if any(term in question_lower for term in _interaction_terms(item))
        ]
        if not relevant:
            relevant = interactions[:3]
        highest = safety.get("highest_severity", "low")
        return {
            "answer": (
                f"Based on the current rule-based safety check, MedGuard found {len(interactions)} "
                f"warning(s). The highest current risk level is {highest}."
            ),
            "recommendation": _recommendation_for_question(question_lower, relevant),
            "related_interactions": relevant,
            "disclaimer": DISCLAIMER,
        }

    return {
        "answer": (
            "I do not see a matching rule-based warning in your current MedGuard list. "
            "That does not guarantee the combination is safe for you personally."
        ),
        "recommendation": "Follow the medicine label and ask a doctor or pharmacist if you are unsure.",
        "related_interactions": [],
        "disclaimer": DISCLAIMER,
    }


def _interaction_terms(interaction: dict[str, Any]) -> list[str]:
    text_parts = [
        interaction.get("interaction_type", ""),
        interaction.get("explanation", ""),
        interaction.get("recommendation", ""),
        " ".join(interaction.get("matched_items", [])),
    ]
    words = " ".join(text_parts).lower().replace("/", " ").replace("-", " ").split()
    return [word.strip(".,:;()[]") for word in words if len(word.strip(".,:;()[]")) >= 4]


def _recommendation_for_question(question: str, interactions: list[dict[str, Any]]) -> str:
    if "alcohol" in question:
        return "Avoid alcohol when a warning is present, and ask a doctor or pharmacist before combining it with medicines."
    if "ibuprofen" in question or "pain" in question or "nsaid" in question:
        return "Check with a doctor or pharmacist before using ibuprofen or another NSAID with your current medicines."
    if "why" in question and interactions:
        return interactions[0].get("recommendation", "Review the warning with a doctor or pharmacist.")
    return "Review the related warnings and ask a doctor or pharmacist before changing how you take medicines."
