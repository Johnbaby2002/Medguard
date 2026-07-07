import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle,
  ClipboardList,
  FlaskConical,
  Leaf,
  Pill,
  UserRound,
  XCircle,
} from "lucide-react";
import { getDashboardSummary } from "../api/dashboard";
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

type Medication = {
  id: string;
  name: string;
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
const medicationsStorageKey = "medguard_medications";
const supplementsStorageKey = "medguard_supplements";
const substancesStorageKey = "medguard_substances";

function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}) {
  return (
    <div className="card stat-card">
      <div className="stat-card-top">
        <p className="stat-card-title">{title}</p>
        <div className="stat-card-icon">{icon}</div>
      </div>
      <p className="stat-card-value">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [substances, setSubstances] = useState<Substance[]>([]);

  const dashboardQuery = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardSummary,
  });

  const historyQuery = useQuery({
    queryKey: ["interaction-history"],
    queryFn: getInteractionHistory,
  });

  useEffect(() => {
    const storedProfile = localStorage.getItem(profileStorageKey);
    const storedReminders = localStorage.getItem(remindersStorageKey);
    const storedMedications = localStorage.getItem(medicationsStorageKey);
    const storedSupplements = localStorage.getItem(supplementsStorageKey);
    const storedSubstances = localStorage.getItem(substancesStorageKey);

    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }

    if (storedReminders) {
      setReminders(JSON.parse(storedReminders));
    }

    if (storedMedications) {
      setMedications(JSON.parse(storedMedications));
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

  const adherenceRate = useMemo(() => {
    if (reminders.length === 0) return 0;

    return Math.round((takenReminders.length / reminders.length) * 100);
  }, [reminders.length, takenReminders.length]);

  const totalInteractions = useMemo(() => {
    return history.reduce((sum, item) => sum + item.interactions.length, 0);
  }, [history]);

  const highestRisk = useMemo(() => {
    if (history.length === 0) return 0;

    return Math.max(...history.map((item) => item.total_risk_score));
  }, [history]);

  const profileStatus = profile ? "Set" : "Empty";

  if (dashboardQuery.isLoading || historyQuery.isLoading) {
    return <p className="loading-text">Loading dashboard...</p>;
  }

  const backendData = dashboardQuery.data;

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Medication safety overview</p>
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Track medications, supplements, substances, reminders, adherence, and
          latest safety risk in one place.
        </p>
      </header>

      <div className="stats-grid">
        <StatCard
          title="Medications"
          value={medications.length || backendData?.active_medications || 0}
          icon={<Pill size={22} />}
        />

        <StatCard
          title="Supplements"
          value={supplements.length || backendData?.supplements || 0}
          icon={<Leaf size={22} />}
        />

        <StatCard
          title="Substances"
          value={substances.length}
          icon={<FlaskConical size={22} />}
        />

        <StatCard
          title="Active reminders"
          value={activeReminders.length || backendData?.active_reminders || 0}
          icon={<Bell size={22} />}
        />

        <StatCard
          title="Taken doses"
          value={takenReminders.length || backendData?.taken_doses || 0}
          icon={<CheckCircle size={22} />}
        />

        <StatCard
          title="Missed doses"
          value={backendData?.missed_doses || 0}
          icon={<XCircle size={22} />}
        />

        <StatCard
          title={`Latest risk ${latestCheck?.highest_severity || backendData?.latest_highest_severity || "none"}`}
          value={
            latestCheck?.total_risk_score ??
            backendData?.latest_total_risk_score ??
            0
          }
          icon={<AlertTriangle size={22} />}
        />

        <StatCard
          title="Safety checks"
          value={history.length}
          icon={<ClipboardList size={22} />}
        />

        <StatCard
          title="Profile"
          value={profileStatus}
          icon={<UserRound size={22} />}
        />
      </div>

      <div className="safety-layout" style={{ marginTop: 24 }}>
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Latest safety summary</h2>
          <p className="safety-panel-text">
            Most recent interaction analysis from your safety history.
          </p>

          {!latestCheck ? (
            <div className="interaction-card" style={{ marginTop: 20 }}>
              <h4 className="interaction-title">No safety checks yet</h4>
              <p className="interaction-description">
                Run a safety check to generate dashboard risk data.
              </p>
            </div>
          ) : (
            <div className="interaction-list" style={{ marginTop: 20 }}>
              <div className="interaction-card">
                <h4 className="interaction-title">Latest result</h4>
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
                <h4 className="interaction-title">Risk trend</h4>
                <p className="risk-label">
                  Highest recorded risk: {highestRisk}
                </p>
                <p className="risk-label">
                  Total interactions found: {totalInteractions}
                </p>
                <p className="risk-label">
                  Total safety checks: {history.length}
                </p>
              </div>

              {latestCheck.recommended_actions.length > 0 && (
                <div className="interaction-card">
                  <h4 className="interaction-title">Recommended actions</h4>
                  <ul className="action-list">
                    {latestCheck.recommended_actions.slice(0, 4).map(
                      (action, index) => (
                        <li key={`${action}-${index}`}>{action}</li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Daily routine</h2>
          <p className="safety-panel-text">
            Reminder activity and adherence stored on this device.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Reminder overview</h4>
              <p className="risk-label">Total reminders: {reminders.length}</p>
              <p className="risk-label">
                Active reminders: {activeReminders.length}
              </p>
              <p className="risk-label">
                Marked taken: {takenReminders.length}
              </p>
              <p className="risk-label">Adherence: {adherenceRate}%</p>
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Tracking overview</h4>
              <p className="risk-label">
                Medications tracked:{" "}
                {medications.length || backendData?.active_medications || 0}
              </p>
              <p className="risk-label">
                Supplements tracked:{" "}
                {supplements.length || backendData?.supplements || 0}
              </p>
              <p className="risk-label">
                Substances tracked: {substances.length}
              </p>
            </div>
          </div>
        </section>
      </div>

      <div className="safety-layout" style={{ marginTop: 24 }}>
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Health profile</h2>
          <p className="safety-panel-text">
            Clinical context used to support safer medication decisions.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Profile context</h4>
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
          </div>
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Tracked lifestyle factors</h2>
          <p className="safety-panel-text">
            Supplements and substances that may affect medication safety.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Supplements</h4>
              {supplements.length === 0 ? (
                <p className="interaction-description">
                  No supplements added yet.
                </p>
              ) : (
                supplements.slice(0, 5).map((item) => (
                  <p className="risk-label" key={item.id}>
                    {item.name} · {item.category}
                  </p>
                ))
              )}
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Substances</h4>
              {substances.length === 0 ? (
                <p className="interaction-description">
                  No substances added yet.
                </p>
              ) : (
                substances.slice(0, 5).map((item) => (
                  <p className="risk-label" key={item.id}>
                    {item.name} · {item.type}
                  </p>
                ))
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}