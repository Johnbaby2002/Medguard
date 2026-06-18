from sqlalchemy.orm import Session

from app.models import InteractionRule, InteractionType, Severity


SEED_RULES = [
    {
        "rule_key": "blood_thinner_nsaid",
        "severity": Severity.high,
        "interaction_type": InteractionType.drug_drug,
        "terms_a": ["warfarin", "blood thinner", "anticoagulant", "apixaban", "rivaroxaban"],
        "terms_b": ["ibuprofen", "naproxen", "aspirin", "nsaid", "painkiller"],
        "explanation": "Combining a blood thinner with an NSAID or painkiller can increase bleeding risk.",
        "recommendation": "Ask a doctor or pharmacist before combining these medicines.",
        "timing_suggestion": "Do not separate only by timing; this combination needs professional review.",
    },
    {
        "rule_key": "sleeping_pill_alcohol",
        "severity": Severity.critical,
        "interaction_type": InteractionType.alcohol,
        "terms_a": ["zolpidem", "sleeping pill", "sedative", "benzodiazepine"],
        "terms_b": ["alcohol"],
        "explanation": "Alcohol with sleeping pills can cause dangerous sedation, slowed breathing, falls, or accidents.",
        "recommendation": "Avoid alcohol and contact a clinician if this combination happened.",
        "timing_suggestion": "Avoid alcohol while using sedating medicines unless a clinician says otherwise.",
    },
    {
        "rule_key": "anxiety_sleeping_pill",
        "severity": Severity.high,
        "interaction_type": InteractionType.sedative_combination,
        "terms_a": ["anxiety medication", "alprazolam", "lorazepam", "diazepam", "benzodiazepine"],
        "terms_b": ["sleeping pill", "zolpidem", "sedative"],
        "explanation": "Anxiety medicines and sleeping pills can add together and cause strong drowsiness or falls.",
        "recommendation": "Use only as prescribed and ask a clinician before combining sedating medicines.",
        "timing_suggestion": "Avoid taking multiple sedating medicines close together unless prescribed.",
    },
    {
        "rule_key": "grapefruit_toxicity",
        "severity": Severity.moderate,
        "interaction_type": InteractionType.grapefruit,
        "terms_a": ["statin", "atorvastatin", "simvastatin", "amlodipine", "medication"],
        "terms_b": ["grapefruit"],
        "explanation": "Grapefruit can raise levels of some medicines and increase side effects.",
        "recommendation": "Check the medication label and ask a pharmacist if grapefruit is safe.",
        "timing_suggestion": "For some medicines, spacing grapefruit is not enough. Avoid until confirmed safe.",
    },
    {
        "rule_key": "antibiotic_birth_control",
        "severity": Severity.moderate,
        "interaction_type": InteractionType.drug_drug,
        "terms_a": ["rifampin", "rifabutin", "antibiotic"],
        "terms_b": ["birth control", "contraceptive", "ethinyl estradiol"],
        "explanation": "Some antibiotics may reduce contraceptive effectiveness.",
        "recommendation": "Ask a clinician whether backup contraception is needed.",
        "timing_suggestion": "Use backup protection if advised by a clinician.",
    },
    {
        "rule_key": "preworkout_anxiety",
        "severity": Severity.moderate,
        "interaction_type": InteractionType.caffeine_preworkout,
        "terms_a": ["pre-workout", "preworkout", "caffeine", "energy drink"],
        "terms_b": ["anxiety medication", "anxiety", "stimulant"],
        "explanation": "High caffeine or pre-workout products can increase heart rate, shakiness, or nervousness.",
        "recommendation": "Reduce stimulant intake and ask a clinician if symptoms occur.",
        "timing_suggestion": "Avoid high caffeine close to anxiety symptoms or stimulant medicines.",
    },
    {
        "rule_key": "cold_medicine_duplicate",
        "severity": Severity.high,
        "interaction_type": InteractionType.duplicate_active_ingredient,
        "terms_a": ["acetaminophen", "paracetamol", "cold medicine", "flu medicine"],
        "terms_b": ["acetaminophen", "paracetamol"],
        "explanation": "Multiple cold medicines can contain the same ingredient, which can lead to overdose.",
        "recommendation": "Compare active ingredients before taking multiple cold or flu products.",
        "timing_suggestion": "Follow maximum daily dose limits on the label.",
    },
]


def seed_interaction_rules(db: Session) -> None:
    for rule_data in SEED_RULES:
        existing = db.query(InteractionRule).filter(InteractionRule.rule_key == rule_data["rule_key"]).first()
        if existing:
            continue
        db.add(InteractionRule(**rule_data))
    db.commit()
