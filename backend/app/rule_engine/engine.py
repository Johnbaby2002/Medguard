from collections import Counter
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import HealthProfile, InteractionRule, InteractionType, Medication, Severity, Substance, Supplement
from app.schemas import MEDICAL_DISCLAIMER, InteractionOut, SafetyCheckResponse


SEVERITY_SCORE = {
    Severity.low: 10,
    Severity.moderate: 25,
    Severity.high: 50,
    Severity.critical: 80,
}


@dataclass
class SafetyContext:
    profile: HealthProfile | None
    medications: list[Medication]
    supplements: list[Supplement]
    substances: list[Substance]


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def item_terms(context: SafetyContext) -> dict[str, list[str]]:
    terms: dict[str, list[str]] = {}
    for medication in context.medications:
        terms[f"medication:{medication.id}"] = [
            "medication",
            "prescription" if medication.is_prescription else "otc medicine",
            normalize(medication.name),
            normalize(medication.active_ingredient),
            normalize(medication.medication_category),
            normalize(medication.notes),
        ]
    for supplement in context.supplements:
        terms[f"supplement:{supplement.id}"] = [
            "supplement",
            normalize(supplement.name),
            normalize(supplement.active_ingredient_category),
            normalize(supplement.notes),
        ]
    for substance in context.substances:
        if not substance.is_active:
            continue
        terms[f"substance:{substance.id}"] = [
            "substance",
            normalize(substance.category.value),
            normalize(substance.category.name),
            normalize(substance.name),
            normalize(substance.active_ingredient),
            normalize(substance.frequency),
            normalize(substance.amount),
            normalize(substance.notes),
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
        values = [
            "medication",
            "prescription" if medication.is_prescription else "otc medicine",
            medication.name,
            medication.active_ingredient,
            medication.medication_category or "",
            medication.notes or "",
        ]
        if contains_any([normalize(value) for value in values], terms_a + terms_b):
            matched.append(medication.name)
    for supplement in context.supplements:
        values = [supplement.name, supplement.active_ingredient_category, supplement.notes or ""]
        if contains_any([normalize(value) for value in values], terms_a + terms_b):
            matched.append(supplement.name)
    for substance in context.substances:
        values = [
            "substance",
            substance.category.value,
            substance.category.name,
            substance.name,
            substance.active_ingredient or "",
            substance.amount or "",
            substance.frequency,
            substance.notes or "",
        ]
        if substance.is_active and contains_any([normalize(value) for value in values], terms_a + terms_b):
            matched.append(substance.name)
    if context.profile:
        profile_values = item_terms(context).get("profile", [])
        if contains_any(profile_values, terms_a + terms_b):
            matched.append("Health profile")
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
    ingredient_items: dict[str, list[str]] = {}
    for medication in context.medications:
        ingredient = normalize(medication.active_ingredient)
        if ingredient:
            ingredient_items.setdefault(ingredient, []).append(medication.name)
    for substance in context.substances:
        ingredient = normalize(substance.active_ingredient)
        if ingredient and substance.is_active:
            ingredient_items.setdefault(ingredient, []).append(substance.name)
    counts = Counter({ingredient: len(items) for ingredient, items in ingredient_items.items()})
    interactions = []
    for ingredient, count in counts.items():
        if ingredient and count > 1:
            interactions.append(
                InteractionOut(
                    severity=Severity.high,
                    interaction_type=InteractionType.duplicate_active_ingredient,
                    explanation=f"Multiple medications contain {ingredient}, which can increase overdose risk.",
                    recommendation="Check medication and OTC labels, and ask a pharmacist before taking duplicate ingredients together.",
                    matched_items=ingredient_items[ingredient],
                )
            )
    return interactions


def duplicate_nsaid_interaction(context: SafetyContext) -> list[InteractionOut]:
    nsaid_terms = {"ibuprofen", "naproxen", "aspirin", "diclofenac", "celecoxib", "nsaid"}
    matches = []
    for med in context.medications:
        if normalize(med.active_ingredient) in nsaid_terms or normalize(med.medication_category) == "nsaid":
            matches.append(med.name)
    for substance in context.substances:
        values = {
            normalize(substance.name),
            normalize(substance.active_ingredient),
            normalize(substance.category.value),
            normalize(substance.notes),
        }
        if substance.is_active and (values & nsaid_terms or "otc_medicine" in values):
            if contains_any(list(values), list(nsaid_terms)):
                matches.append(substance.name)
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

    score = min(100, sum(SEVERITY_SCORE[interaction.severity] for interaction in interactions))
    highest = Severity.low
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
