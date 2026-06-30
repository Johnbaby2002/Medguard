import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Bell, ClipboardList, UserRound } from "lucide-react";
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

const profileStorageKey = "medguard_health_profile";
const remindersStorageKey = "medguard_reminders";

export default function ReportsPage() {
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);

  const historyQuery = useQuery({
    queryKey: ["interaction-history"],
    queryFn: getInteractionHistory,
  });

  useEffect(() => {
    const storedProfile = localStorage.getItem(profileStorageKey);
    const storedReminders = localStorage.getItem(remindersStorageKey);

    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }

    if (storedReminders) {
      setReminders(JSON.parse(storedReminders));
    }
  }, []);

  const history = historyQuery.data ?? [];
  const latestCheck = history[0];

  const activeReminders = reminders.filter((reminder) => !reminder.taken);
  const takenReminders = reminders.filter((reminder) => reminder.taken);

  const highestRisk = useMemo(() => {
    if (history.length === 0) return 0;

    return Math.max(...history.map((item) => item.total_risk_score));
  }, [history]);

  const totalInteractions = useMemo(() => {
    return history.reduce((sum, item) => sum + item.interactions.length, 0);
  }, [history]);

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Health insights</p>
        <h1 className="page-title">Reports</h1>
        <p className="page-description">
          Review safety trends, reminder activity, and health profile context.
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
              <h2 className="stat-value">{profile ? "Set" : "Empty"}</h2>
            </div>
            <div className="stat-card-icon">
              <UserRound size={22} />
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
                <p className="risk-label">Highest recorded risk: {highestRisk}</p>
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
              <p className="risk-label">
                Age: {profile?.age || "Not set"}
              </p>
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
    </div>
  );
}