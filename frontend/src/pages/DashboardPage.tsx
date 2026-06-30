import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, Bell, CheckCircle, Pill, XCircle } from "lucide-react";
import { getDashboardSummary } from "../api/dashboard";

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
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardSummary,
  });

  if (isLoading) {
    return <p className="loading-text">Loading dashboard...</p>;
  }

  if (error || !data) {
    return <p className="error-text">Could not load dashboard.</p>;
  }

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Medication safety overview</p>
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Track active medications, reminders, adherence, and latest safety risk.
        </p>
      </header>

      <div className="stats-grid">
        <StatCard title="Active medications" value={data.active_medications} icon={<Pill size={22} />} />
        <StatCard title="Supplements" value={data.supplements} icon={<Activity size={22} />} />
        <StatCard title="Active reminders" value={data.active_reminders} icon={<Bell size={22} />} />
        <StatCard title="Taken doses" value={data.taken_doses} icon={<CheckCircle size={22} />} />
        <StatCard title="Missed doses" value={data.missed_doses} icon={<XCircle size={22} />} />
        <StatCard
          title={`Latest risk ${data.latest_highest_severity ?? "none"}`}
          value={data.latest_total_risk_score}
          icon={<AlertTriangle size={22} />}
        />
      </div>
    </div>
  );
}