import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bell,
  ClipboardList,
  FlaskConical,
  Leaf,
  UserRound,
} from "lucide-react";
import { getInteractionHistory } from "../api/history";

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

type Reminder = {
  id: string;
  medicationName: string;
  dosage: string;
  time: string;
  frequency: string;
  notes: string;
  taken: boolean;
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

const profileStorageKey = "medguard_health_profile";
const remindersStorageKey = "medguard_reminders";
const supplementsStorageKey = "medguard_supplements";
const substancesStorageKey = "medguard_substances";

export default function ReportsPage() {
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [substances, setSubstances] = useState<Substance[]>([]);

  const historyQuery = useQuery({
    queryKey: ["interaction-history"],
    queryFn: getInteractionHistory,
  });

  useEffect(() => {
    const storedProfile = localStorage.getItem(profileStorageKey);
    const storedReminders = localStorage.getItem(remindersStorageKey);
    const storedSupplements = localStorage.getItem(supplementsStorageKey);
    const storedSubstances = localStorage.getItem(substancesStorageKey);

    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }

    if (storedReminders) {
      setReminders(JSON.parse(storedReminders));
    }

    if (storedSupplements) {
      setSupplements(JSON.parse(storedSupplements));
    }

    if (storedSubstances) {
      setSubstances(JSON.parse(storedSubstances));
    }
  }, []);

  const history = historyQuery.data ?? [];
  const latestCheck = history[0];

  const activeReminders = reminders.filter((reminder) => !reminder.taken);
  const takenReminders = reminders.filter((reminder) => reminder.taken);

  const dailySupplements = supplements.filter((item) =>
    item.frequency.toLowerCase().includes("daily")
  );

  const dailySubstances = substances.filter((item) =>
    item.frequency.toLowerCase().includes("daily")
  );

  const highestRisk = useMemo(() => {
    if (history.length === 0) return 0;

    return Math.max(...history.map((item) => item.total_risk_score));
  }, [history]);

  const totalInteractions = useMemo(() => {
    return history.reduce((sum, item) => sum + item.interactions.length, 0);
  }, [history]);

  const profileCompleteness = useMemo(() => {
    if (!profile) return 0;

    const fields = [
      profile.age,
      profile.weight,
      profile.sex,
      profile.pregnant,
      profile.kidneyDisease,
      profile.liverDisease,
      profile.allergies,
      profile.conditions,
      profile.notes,
    ];

    const completedFields = fields.filter(
      (field) => field && field.trim().length > 0
    ).length;

    return Math.round((completedFields / fields.length) * 100);
  }, [profile]);

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Health insights</p>
        <h1 className="page-title">Reports</h1>
        <p className="page-description">
          Review safety trends, reminder activity, supplements, substances, and
          health profile context.
        </p>
      </header>

      <div className="stats-grid">
        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Safety checks</p>
              <h2 className="stat-value">{history.length}</h2>
            </div>
            <div className="stat-card-icon">
              <ClipboardList size={22} />
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Latest risk score</p>
              <h2 className="stat-value">
                {latestCheck ? latestCheck.total_risk_score : 0}
              </h2>
            </div>
            <div className="stat-card-icon">
              <AlertTriangle size={22} />
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Reminders</p>
              <h2 className="stat-value">{reminders.length}</h2>
            </div>
            <div className="stat-card-icon">
              <Bell size={22} />
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Profile</p>
              <h2 className="stat-value">
                {profile ? `${profileCompleteness}%` : "Empty"}
              </h2>
            </div>
            <div className="stat-card-icon">
              <UserRound size={22} />
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Supplements</p>
              <h2 className="stat-value">{supplements.length}</h2>
            </div>
            <div className="stat-card-icon">
              <Leaf size={22} />
            </div>
          </div>
        </section>

        <section className="card stat-card">
          <div className="stat-card-top">
            <div>
              <p className="stat-label">Substances</p>
              <h2 className="stat-value">{substances.length}</h2>
            </div>
            <div className="stat-card-icon">
              <FlaskConical size={22} />
            </div>
          </div>
        </section>
      </div>

      <div className="safety-layout" style={{ marginTop: 24 }}>
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Safety report</h2>
          <p className="safety-panel-text">
            Summary based on previous interaction checks.
          </p>

          {historyQuery.isLoading && (
            <p className="safety-panel-text" style={{ marginTop: 18 }}>
              Loading safety report...
            </p>
          )}

          {!historyQuery.isLoading && history.length === 0 && (
            <div className="interaction-card" style={{ marginTop: 20 }}>
              <h4 className="interaction-title">No safety checks yet</h4>
              <p className="interaction-description">
                Run a safety check to generate risk report data.
              </p>
            </div>
          )}

          {latestCheck && (
            <div className="interaction-list" style={{ marginTop: 20 }}>
              <div className="interaction-card">
                <h4 className="interaction-title">Latest analysis</h4>
                <p className="risk-label">
                  Risk score: {latestCheck.total_risk_score}
                </p>
                <p className="risk-label">
                  Highest severity: {latestCheck.highest_severity || "none"}
                </p>
                <p className="risk-label">
                  Date: {new Date(latestCheck.created_at).toLocaleString()}
                </p>
              </div>

              <div className="interaction-card">
                <h4 className="interaction-title">Overall trend</h4>
                <p className="risk-label">
                  Highest recorded risk: {highestRisk}
                </p>
                <p className="risk-label">
                  Total interactions found: {totalInteractions}
                </p>
                <p className="risk-label">
                  Total checks completed: {history.length}
                </p>
              </div>

              {latestCheck.recommended_actions.length > 0 && (
                <div className="interaction-card">
                  <h4 className="interaction-title">Recommended actions</h4>
                  <ul className="action-list">
                    {latestCheck.recommended_actions.map((action, index) => (
                      <li key={`${action}-${index}`}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Medication routine</h2>
          <p className="safety-panel-text">
            Reminder progress stored on this device.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Reminder status</h4>
              <p className="risk-label">Total reminders: {reminders.length}</p>
              <p className="risk-label">
                Active reminders: {activeReminders.length}
              </p>
              <p className="risk-label">
                Marked taken: {takenReminders.length}
              </p>
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Health profile context</h4>
              <p className="risk-label">Age: {profile?.age || "Not set"}</p>
              <p className="risk-label">
                Weight: {profile?.weight ? `${profile.weight} kg` : "Not set"}
              </p>
              <p className="risk-label">
                Sex: {profile?.sex || "Not specified"}
              </p>
              <p className="risk-label">
                Pregnant: {profile?.pregnant || "No"}
              </p>
              <p className="risk-label">
                Kidney disease: {profile?.kidneyDisease || "No"}
              </p>
              <p className="risk-label">
                Liver disease: {profile?.liverDisease || "No"}
              </p>
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Clinical notes</h4>
              <p className="interaction-description">
                <strong>Allergies:</strong>{" "}
                {profile?.allergies || "None added"}
              </p>
              <p className="interaction-description" style={{ marginTop: 8 }}>
                <strong>Conditions:</strong>{" "}
                {profile?.conditions || "None added"}
              </p>
              <p className="interaction-description" style={{ marginTop: 8 }}>
                <strong>Notes:</strong> {profile?.notes || "None added"}
              </p>
            </div>
          </div>
        </section>
      </div>

      <div className="safety-layout" style={{ marginTop: 24 }}>
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Supplements overview</h2>
          <p className="safety-panel-text">
            Vitamins, minerals, herbal products, and other supplement items
            stored on this device.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Supplement summary</h4>
              <p className="risk-label">
                Total supplements: {supplements.length}
              </p>
              <p className="risk-label">
                Daily supplements: {dailySupplements.length}
              </p>
              <p className="risk-label">
                Categories:{" "}
                {new Set(supplements.map((item) => item.category)).size}
              </p>
            </div>

            {supplements.length === 0 ? (
              <div className="interaction-card">
                <h4 className="interaction-title">No supplements added</h4>
                <p className="interaction-description">
                  Add supplements to improve report quality.
                </p>
              </div>
            ) : (
              supplements.slice(0, 5).map((item) => (
                <div className="interaction-card" key={item.id}>
                  <h4 className="interaction-title">{item.name}</h4>
                  <p className="risk-label">Category: {item.category}</p>
                  <p className="risk-label">
                    Dose: {item.dose || "Not specified"}
                  </p>
                  <p className="risk-label">
                    Frequency: {item.frequency || "Not specified"}
                  </p>
                  {item.notes && (
                    <p className="interaction-description">{item.notes}</p>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Substances overview</h2>
          <p className="safety-panel-text">
            Alcohol, caffeine, nicotine, grapefruit, OTC medicines, and other
            lifestyle factors stored on this device.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Substance summary</h4>
              <p className="risk-label">
                Total substances: {substances.length}
              </p>
              <p className="risk-label">
                Daily substances: {dailySubstances.length}
              </p>
              <p className="risk-label">
                Types: {new Set(substances.map((item) => item.type)).size}
              </p>
            </div>

            {substances.length === 0 ? (
              <div className="interaction-card">
                <h4 className="interaction-title">No substances added</h4>
                <p className="interaction-description">
                  Add substances to improve lifestyle risk reporting.
                </p>
              </div>
            ) : (
              substances.slice(0, 5).map((item) => (
                <div className="interaction-card" key={item.id}>
                  <h4 className="interaction-title">{item.name}</h4>
                  <p className="risk-label">Type: {item.type}</p>
                  <p className="risk-label">
                    Amount: {item.amount || "Not specified"}
                  </p>
                  <p className="risk-label">
                    Frequency: {item.frequency || "Not specified"}
                  </p>
                  {item.notes && (
                    <p className="interaction-description">{item.notes}</p>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}