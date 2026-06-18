from collections import Counter
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import HealthProfile, InteractionRule, InteractionType, Medication, Severity, Supplement
from app.schemas import MEDICAL_DISCLAIMER, InteractionOut, SafetyCheckResponse


SEVERITY_SCORE = {
    Severity.low: 1,
    Severity.moderate: 3,
    Severity.high: 6,
    Severity.critical: 10,
}


@dataclass
class SafetyContext:
    profile: HealthProfile | None
    medications: list[Medication]
    supplements: list[Supplement]


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def item_terms(context: SafetyContext) -> dict[str, list[str]]:
    terms: dict[str, list[str]] = {}
    for medication in context.medications:
        terms[f"medication:{medication.id}"] = [
            normalize(medication.name),
            normalize(medication.active_ingredient),
            normalize(medication.medication_category),
            normalize(medication.notes),
        ]
    for supplement in context.supplements:
        terms[f"supplement:{supplement.id}"] = [
            normalize(supplement.name),
            normalize(supplement.active_ingredient_category),
            normalize(supplement.notes),
        ]
    profile_terms = []
    if context.profile:
        profile_terms = [
            normalize(context.profile.alcohol_use),
            normalize(context.profile.caffeine_preworkout_use),
            *[normalize(condition) for condition in context.profile.known_conditions],
            *[normalize(allergy) for allergy in context.profile.allergies],
        ]
        if context.profile.alcohol_use and context.profile.alcohol_use.lower() not in {"none", "no"}:
            profile_terms.append("alcohol")
        if context.profile.caffeine_preworkout_use and context.profile.caffeine_preworkout_use.lower() not in {"none", "no"}:
            profile_terms.extend(["caffeine", "pre-workout"])
    terms["profile"] = profile_terms
    return terms


def contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = " ".join(values)
    return any(normalize(needle) and normalize(needle) in haystack for needle in needles)


def matched_item_names(context: SafetyContext, terms_a: list[str], terms_b: list[str]) -> list[str]:
    matched = []
    for medication in context.medications:
        values = [medication.name, medication.active_ingredient, medication.medication_category or "", medication.notes or ""]
        if contains_any([normalize(value) for value in values], terms_a + terms_b):
            matched.append(medication.name)
    for supplement in context.supplements:
        values = [supplement.name, supplement.active_ingredient_category, supplement.notes or ""]
        if contains_any([normalize(value) for value in values], terms_a + terms_b):
            matched.append(supplement.name)
    return sorted(set(matched))


def rule_matches(rule: InteractionRule, context: SafetyContext) -> bool:
    terms_by_item = item_terms(context)
    all_values = [value for values in terms_by_item.values() for value in values]
    has_a = contains_any(all_values, rule.terms_a)
    if not rule.terms_b:
        return has_a
    has_b = contains_any(all_values, rule.terms_b)
    return has_a and has_b


def duplicate_active_ingredient_interactions(context: SafetyContext) -> list[InteractionOut]:
    counts = Counter(normalize(med.active_ingredient) for med in context.medications)
    interactions = []
    for ingredient, count in counts.items():
        if ingredient and count > 1:
            interactions.append(
                InteractionOut(
                    severity=Severity.high,
                    interaction_type=InteractionType.duplicate_active_ingredient,
                    explanation=f"Multiple medications contain {ingredient}, which can increase overdose risk.",
                    recommendation="Check labels and ask a pharmacist before taking duplicate ingredients together.",
                    matched_items=[
                        med.name for med in context.medications if normalize(med.active_ingredient) == ingredient
                    ],
                )
            )
    return interactions


def duplicate_nsaid_interaction(context: SafetyContext) -> list[InteractionOut]:
    nsaid_terms = {"ibuprofen", "naproxen", "aspirin", "diclofenac", "nsaid"}
    matches = [
        med.name
        for med in context.medications
        if normalize(med.active_ingredient) in nsaid_terms or normalize(med.medication_category) == "nsaid"
    ]
    if len(matches) < 2:
        return []
    return [
        InteractionOut(
            severity=Severity.high,
            interaction_type=InteractionType.nsaid_duplication,
            explanation="Taking multiple NSAID painkillers can increase stomach bleeding and kidney risk.",
            recommendation="Use one NSAID at a time unless a clinician specifically says otherwise.",
            matched_items=matches,
        )
    ]


def analyze_safety(db: Session, context: SafetyContext) -> SafetyCheckResponse:
    rules = db.query(InteractionRule).filter(InteractionRule.is_active.is_(True)).all()
    interactions: list[InteractionOut] = []
    timing_suggestions: list[str] = []

    for rule in rules:
        if not rule_matches(rule, context):
            continue
        interactions.append(
            InteractionOut(
                severity=rule.severity,
                interaction_type=rule.interaction_type,
                explanation=rule.explanation,
                recommendation=rule.recommendation,
                matched_items=matched_item_names(context, rule.terms_a, rule.terms_b),
            )
        )
        if rule.timing_suggestion:
            timing_suggestions.append(rule.timing_suggestion)

    interactions.extend(duplicate_active_ingredient_interactions(context))
    interactions.extend(duplicate_nsaid_interaction(context))

    score = sum(SEVERITY_SCORE[interaction.severity] for interaction in interactions)
    highest = None
    if interactions:
        highest = max((interaction.severity for interaction in interactions), key=lambda severity: SEVERITY_SCORE[severity])
    actions = sorted({interaction.recommendation for interaction in interactions})
    if not actions:
        actions = ["No rule-based warnings detected. Keep following the label and clinician instructions."]

    return SafetyCheckResponse(
        total_risk_score=score,
        interactions=interactions,
        highest_severity=highest,
        recommended_actions=actions,
        safe_timing_suggestions=sorted(set(timing_suggestions)),
        disclaimer=MEDICAL_DISCLAIMER,
    )
