import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ShieldCheck } from "lucide-react";
import { getInteractionHistory } from "../api/history";
import { runSafetyCheck } from "../api/safety";

type HealthProfile = {
  age?: string;
  weight?: string;
  sex?: string;
  pregnant?: string;
  kidneyDisease?: string;
  liverDisease?: string;
  allergies?: string;
  conditions?: string;
  notes?: string;
};

type Medication = {
  id: string;
  name: string;
  dosage?: string;
  frequency?: string;
  notes?: string;
};

type Supplement = {
  id: string;
  name: string;
  category: string;
  dose: string;
  frequency: string;
  notes: string;
};

type Substance = {
  id: string;
  name: string;
  type: string;
  amount: string;
  frequency: string;
  notes: string;
};

type LocalWarning = {
  title: string;
  severity: "low" | "moderate" | "high" | "critical";
  matchedItems: string[];
  explanation: string;
  recommendation: string;
};

const medicationsStorageKey = "medguard_medications";
const profileStorageKey = "medguard_health_profile";
const supplementsStorageKey = "medguard_supplements";
const substancesStorageKey = "medguard_substances";

function formatInteractionType(type: string) {
  const labels: Record<string, string> = {
    drug_drug: "Drug Interaction",
    duplicate_active_ingredient: "Duplicate Active Ingredient",
    nsaid_duplication: "NSAID Duplication",
  };

  return labels[type] ?? type.replaceAll("_", " ");
}

function normalize(value: string) {
  return value.trim().toLowerCase();
}

function includesAny(value: string, keywords: string[]) {
  const normalized = normalize(value);
  return keywords.some((keyword) => normalized.includes(keyword));
}

function severityScore(severity: LocalWarning["severity"]) {
  const scores = {
    low: 2,
    moderate: 5,
    high: 8,
    critical: 12,
  };

  return scores[severity];
}

function getHighestLocalSeverity(warnings: LocalWarning[]) {
  const order: Record<LocalWarning["severity"], number> = {
    low: 1,
    moderate: 2,
    high: 3,
    critical: 4,
  };

  if (warnings.length === 0) return "none";

  return warnings.reduce((highest, warning) =>
    order[warning.severity] > order[highest.severity] ? warning : highest
  ).severity;
}

function buildLocalWarnings(
  medications: Medication[],
  supplements: Supplement[],
  substances: Substance[],
  profile: HealthProfile | null
) {
  const warnings: LocalWarning[] = [];

  const medicationNames = medications.map((item) => item.name);
  const supplementNames = supplements.map((item) => item.name);
  const substanceNames = substances.map((item) => item.name);

  const hasMedication = (keywords: string[]) =>
    medicationNames.some((name) => includesAny(name, keywords));

  const hasSupplement = (keywords: string[]) =>
    supplementNames.some((name) => includesAny(name, keywords));

  const hasSubstance = (keywords: string[]) =>
    substanceNames.some((name) => includesAny(name, keywords));

  const matchedMedications = (keywords: string[]) =>
    medicationNames.filter((name) => includesAny(name, keywords));

  const matchedSupplements = (keywords: string[]) =>
    supplementNames.filter((name) => includesAny(name, keywords));

  const matchedSubstances = (keywords: string[]) =>
    substanceNames.filter((name) => includesAny(name, keywords));

  const alcoholKeywords = ["alcohol", "beer", "wine", "vodka", "whiskey"];
  const grapefruitKeywords = ["grapefruit", "grapefruit juice"];
  const caffeineKeywords = ["caffeine", "coffee", "energy drink", "espresso"];
  const nicotineKeywords = ["nicotine", "cigarette", "smoking", "vape"];

  const warfarinKeywords = ["warfarin", "coumadin"];
  const nsaidKeywords = ["ibuprofen", "naproxen", "aspirin", "diclofenac"];
  const statinKeywords = ["atorvastatin", "simvastatin", "lovastatin"];
  const stimulantKeywords = ["adderall", "methylphenidate", "ritalin", "vyvanse"];
  const bloodPressureKeywords = [
    "amlodipine",
    "lisinopril",
    "metoprolol",
    "losartan",
    "atenolol",
  ];

  if (hasSubstance(alcoholKeywords) && hasMedication(warfarinKeywords)) {
    warnings.push({
      title: "Alcohol + Warfarin",
      severity: "high",
      matchedItems: [
        ...matchedSubstances(alcoholKeywords),
        ...matchedMedications(warfarinKeywords),
      ],
      explanation:
        "Alcohol may increase bleeding risk and can make warfarin effects less predictable.",
      recommendation:
        "Avoid heavy alcohol use and ask a doctor or pharmacist before combining alcohol with warfarin.",
    });
  }

  if (hasSubstance(alcoholKeywords) && hasMedication(nsaidKeywords)) {
    warnings.push({
      title: "Alcohol + NSAID pain reliever",
      severity: "moderate",
      matchedItems: [
        ...matchedSubstances(alcoholKeywords),
        ...matchedMedications(nsaidKeywords),
      ],
      explanation:
        "Alcohol with NSAIDs such as ibuprofen, aspirin, or naproxen may increase stomach bleeding or irritation risk.",
      recommendation:
        "Avoid alcohol around NSAID use unless a clinician says it is safe.",
    });
  }

  if (hasSubstance(grapefruitKeywords) && hasMedication(statinKeywords)) {
    warnings.push({
      title: "Grapefruit + statin",
      severity: "high",
      matchedItems: [
        ...matchedSubstances(grapefruitKeywords),
        ...matchedMedications(statinKeywords),
      ],
      explanation:
        "Grapefruit can increase levels of some statins and may raise the risk of side effects.",
      recommendation:
        "Ask a pharmacist whether grapefruit is safe with this statin.",
    });
  }

  if (
    hasSubstance(grapefruitKeywords) &&
    hasMedication(["amlodipine", "nifedipine", "felodipine"])
  ) {
    warnings.push({
      title: "Grapefruit + blood pressure medication",
      severity: "moderate",
      matchedItems: [
        ...matchedSubstances(grapefruitKeywords),
        ...matchedMedications(["amlodipine", "nifedipine", "felodipine"]),
      ],
      explanation:
        "Grapefruit may increase the effect of some calcium channel blockers.",
      recommendation:
        "Check with a pharmacist before drinking grapefruit juice with this medication.",
    });
  }

  if (hasSubstance(caffeineKeywords) && hasMedication(stimulantKeywords)) {
    warnings.push({
      title: "Caffeine + stimulant medication",
      severity: "moderate",
      matchedItems: [
        ...matchedSubstances(caffeineKeywords),
        ...matchedMedications(stimulantKeywords),
      ],
      explanation:
        "Caffeine may increase stimulant side effects such as anxiety, fast heartbeat, or insomnia.",
      recommendation:
        "Limit caffeine and monitor for sleep problems, palpitations, or nervousness.",
    });
  }

  if (hasSubstance(nicotineKeywords) && hasMedication(bloodPressureKeywords)) {
    warnings.push({
      title: "Nicotine + blood pressure treatment",
      severity: "moderate",
      matchedItems: [
        ...matchedSubstances(nicotineKeywords),
        ...matchedMedications(bloodPressureKeywords),
      ],
      explanation:
        "Nicotine can raise heart rate and blood pressure, which may work against blood pressure treatment.",
      recommendation:
        "Discuss nicotine use with a clinician when using blood pressure medication.",
    });
  }

  if (hasSupplement(["st john", "st. john"]) && medicationNames.length > 0) {
    warnings.push({
      title: "St. John's Wort interaction risk",
      severity: "high",
      matchedItems: matchedSupplements(["st john", "st. john"]),
      explanation:
        "St. John's Wort can interact with many prescription medicines by changing how the body processes them.",
      recommendation:
        "Ask a pharmacist before combining St. John's Wort with any prescription medication.",
    });
  }

  if (hasSupplement(["ginkgo"]) && hasMedication(["warfarin", "aspirin"])) {
    warnings.push({
      title: "Ginkgo + bleeding risk medicine",
      severity: "moderate",
      matchedItems: [
        ...matchedSupplements(["ginkgo"]),
        ...matchedMedications(["warfarin", "aspirin"]),
      ],
      explanation:
        "Ginkgo may increase bleeding risk when combined with blood thinners or aspirin.",
      recommendation:
        "Avoid this combination unless approved by a clinician.",
    });
  }

  if (profile?.pregnant === "Yes" && medications.length > 0) {
    warnings.push({
      title: "Pregnancy medication review needed",
      severity: "high",
      matchedItems: medicationNames,
      explanation:
        "Pregnancy can change medication safety and dosing considerations.",
      recommendation:
        "Review all current medications and supplements with a clinician.",
    });
  }

  if (profile?.kidneyDisease === "Yes" && hasMedication(nsaidKeywords)) {
    warnings.push({
      title: "Kidney disease + NSAID",
      severity: "high",
      matchedItems: matchedMedications(nsaidKeywords),
      explanation:
        "NSAIDs may worsen kidney function in people with kidney disease.",
      recommendation:
        "Avoid NSAIDs unless a clinician specifically says they are safe.",
    });
  }

  if (profile?.liverDisease === "Yes" && hasMedication(["acetaminophen", "paracetamol"])) {
    warnings.push({
      title: "Liver disease + acetaminophen",
      severity: "high",
      matchedItems: matchedMedications(["acetaminophen", "paracetamol"]),
      explanation:
        "Acetaminophen can be risky in liver disease, especially at higher doses.",
      recommendation:
        "Ask a clinician about safe dosing before using acetaminophen.",
    });
  }

  return warnings;
}

export default function SafetyPage() {
  const queryClient = useQueryClient();

  const [medications, setMedications] = useState<Medication[]>([]);
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [substances, setSubstances] = useState<Substance[]>([]);
  const [profile, setProfile] = useState<HealthProfile | null>(null);

  const historyQuery = useQuery({
    queryKey: ["interaction-history"],
    queryFn: getInteractionHistory,
  });

  const safetyMutation = useMutation({
    mutationFn: runSafetyCheck,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interaction-history"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  useEffect(() => {
    const storedMedications = localStorage.getItem(medicationsStorageKey);
    const storedSupplements = localStorage.getItem(supplementsStorageKey);
    const storedSubstances = localStorage.getItem(substancesStorageKey);
    const storedProfile = localStorage.getItem(profileStorageKey);

    if (storedMedications) {
      setMedications(JSON.parse(storedMedications));
    }

    if (storedSupplements) {
      setSupplements(JSON.parse(storedSupplements));
    }

    if (storedSubstances) {
      setSubstances(JSON.parse(storedSubstances));
    }

    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }
  }, []);

  const history = historyQuery.data ?? [];
  const latestHistory = history[0];
  const result = safetyMutation.data ?? latestHistory;

  const localWarnings = useMemo(
    () => buildLocalWarnings(medications, supplements, substances, profile),
    [medications, supplements, substances, profile]
  );

  const localRiskScore = useMemo(() => {
    return localWarnings.reduce(
      (sum, warning) => sum + severityScore(warning.severity),
      0
    );
  }, [localWarnings]);

  const combinedRiskScore = (result?.total_risk_score ?? 0) + localRiskScore;
  const localHighestSeverity = getHighestLocalSeverity(localWarnings);

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Interaction analysis</p>
        <h1 className="page-title">Safety Check</h1>
        <p className="page-description">
          Check medications, supplements, substances, and profile risk factors
          for possible interaction risks.
        </p>
      </header>

      <div className="stats-grid" style={{ marginBottom: 24 }}>
        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Medications</p>
              <h2 className="stat-value">{medications.length}</h2>
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Supplements</p>
              <h2 className="stat-value">{supplements.length}</h2>
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Substances</p>
              <h2 className="stat-value">{substances.length}</h2>
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Local warnings</p>
              <h2 className="stat-value">{localWarnings.length}</h2>
            </div>
          </div>
        </section>
      </div>

      <div className="safety-layout">
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Run safety analysis</h2>
          <p className="safety-panel-text">
            MedGuard will analyze your current medications, supplements,
            substances, lifestyle factors, and health profile.
          </p>

          <button
            className="primary-button"
            disabled={safetyMutation.isPending}
            onClick={() => safetyMutation.mutate()}
          >
            <ShieldCheck size={18} />
            {safetyMutation.isPending ? "Checking..." : "Run safety check"}
          </button>

          {safetyMutation.isSuccess && (
            <p className="safety-panel-text" style={{ marginTop: 14 }}>
              Safety check completed. Local lifestyle warnings are shown below.
            </p>
          )}

          {safetyMutation.isError && (
            <p className="error-text">Could not run safety check.</p>
          )}

          <h3 className="card-title" style={{ marginTop: 30 }}>
            Previous checks
          </h3>

          {historyQuery.isLoading && (
            <p className="safety-panel-text">Loading history...</p>
          )}

          {!historyQuery.isLoading && history.length === 0 && (
            <p className="safety-panel-text">No previous checks yet.</p>
          )}

          <div className="history-list">
            {history.slice(0, 5).map((item) => (
              <div className="history-item" key={item.id}>
                <div>
                  <div className="history-score">{item.total_risk_score}</div>
                  <div className="history-meta">
                    Severity: {item.highest_severity || "none"}
                  </div>
                </div>

                <div className="history-meta">
                  {new Date(item.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="card safety-panel">
          {!result && localWarnings.length === 0 && (
            <div>
              <h2 className="safety-panel-title">No result yet</h2>
              <p className="safety-panel-text">
                Run a safety check or add substances and supplements to see risk
                warnings.
              </p>
            </div>
          )}

          {(result || localWarnings.length > 0) && (
            <div>
              <div className="stat-card-top">
                <div>
                  <h2 className="safety-panel-title">Latest result</h2>
                  <p className="risk-label">
                    Backend severity: {result?.highest_severity || "none"}
                  </p>
                  <p className="risk-label">
                    Local severity: {localHighestSeverity}
                  </p>
                </div>

                <div className="stat-card-icon">
                  <AlertTriangle size={22} />
                </div>
              </div>

              <div className="risk-score">{combinedRiskScore}</div>
              <div className="risk-label">combined risk score</div>

              {result && (
                <>
                  <h3 className="card-title" style={{ marginTop: 28 }}>
                    Medication interactions
                  </h3>

                  {result.interactions.length === 0 ? (
                    <p className="safety-panel-text">
                      No medication interactions found by backend.
                    </p>
                  ) : (
                    <div className="interaction-list">
                      {result.interactions.map((interaction, index) => (
                        <div
                          className="interaction-card"
                          key={`${interaction.interaction_type}-${index}`}
                        >
                          <h4 className="interaction-title">
                            {formatInteractionType(
                              interaction.interaction_type
                            )}{" "}
                            · {interaction.severity}
                          </h4>

                          {interaction.matched_items.length > 0 && (
                            <p className="risk-label">
                              Matched: {interaction.matched_items.join(", ")}
                            </p>
                          )}

                          <p className="interaction-description">
                            {interaction.explanation}
                          </p>

                          <p
                            className="interaction-description"
                            style={{ marginTop: 10 }}
                          >
                            <strong>Recommendation:</strong>{" "}
                            {interaction.recommendation}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

              <h3 className="card-title" style={{ marginTop: 28 }}>
                Lifestyle & profile warnings
              </h3>

              {localWarnings.length === 0 ? (
                <p className="safety-panel-text">
                  No lifestyle or profile warnings found.
                </p>
              ) : (
                <div className="interaction-list">
                  {localWarnings.map((warning, index) => (
                    <div
                      className="interaction-card"
                      key={`${warning.title}-${index}`}
                    >
                      <h4 className="interaction-title">
                        {warning.title} · {warning.severity}
                      </h4>

                      {warning.matchedItems.length > 0 && (
                        <p className="risk-label">
                          Matched: {warning.matchedItems.join(", ")}
                        </p>
                      )}

                      <p className="interaction-description">
                        {warning.explanation}
                      </p>

                      <p
                        className="interaction-description"
                        style={{ marginTop: 10 }}
                      >
                        <strong>Recommendation:</strong>{" "}
                        {warning.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {result && result.safe_timing_suggestions.length > 0 && (
                <>
                  <h3 className="card-title" style={{ marginTop: 28 }}>
                    Safe timing suggestions
                  </h3>
                  <ul className="action-list">
                    {result.safe_timing_suggestions.map(
                      (suggestion, index) => (
                        <li key={`${suggestion}-${index}`}>{suggestion}</li>
                      )
                    )}
                  </ul>
                </>
              )}

              <p className="safety-panel-text" style={{ marginTop: 28 }}>
                {result?.disclaimer ||
                  "This report is for educational support only and does not replace medical advice."}
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}