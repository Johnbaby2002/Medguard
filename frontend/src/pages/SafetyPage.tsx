import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ShieldCheck } from "lucide-react";
import { getInteractionHistory } from "../api/history";
import { runSafetyCheck } from "../api/safety";

function formatInteractionType(type: string) {
  const labels: Record<string, string> = {
    drug_drug: "Drug Interaction",
    duplicate_active_ingredient: "Duplicate Active Ingredient",
    nsaid_duplication: "NSAID Duplication",
  };

  return labels[type] ?? type.replaceAll("_", " ");
}

export default function SafetyPage() {
  const queryClient = useQueryClient();

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
  
  const history = historyQuery.data ?? [];
  const latestHistory = history[0];
  const result = safetyMutation.data ?? latestHistory;


  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Interaction analysis</p>
        <h1 className="page-title">Safety Check</h1>
        <p className="page-description">
          Check medications and supplements for possible interaction risks.
        </p>
      </header>

      <div className="safety-layout">
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Run safety analysis</h2>
          <p className="safety-panel-text">
            MedGuard will analyze your current medications and supplements using
            the active health profile and rule engine.
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
                Safety check completed and saved to history.
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
          {!result && (
            <div>
              <h2 className="safety-panel-title">No result yet</h2>
              <p className="safety-panel-text">
                Run a safety check to see risk score, interactions, and recommended actions.
              </p>
            </div>
          )}

          {result && (
            <div>
              <div className="stat-card-top">
                <div>
                  <h2 className="safety-panel-title">Latest result</h2>
                  <p className="risk-label">
                    Highest severity: {result.highest_severity || "none"}
                  </p>
                </div>

                <div className="stat-card-icon">
                  <AlertTriangle size={22} />
                </div>
              </div>

              <div className="risk-score">{result.total_risk_score}</div>
              <div className="risk-label">total risk score</div>

              <h3 className="card-title" style={{ marginTop: 28 }}>
                Interactions
              </h3>

              {result.interactions.length === 0 ? (
                <p className="safety-panel-text">No interactions found.</p>
              ) : (
                <div className="interaction-list">
                  {result.interactions.map((interaction, index) => (
                    <div
                      className="interaction-card"
                      key={`${interaction.interaction_type}-${index}`}
                    >
                      <h4 className="interaction-title">
                        {formatInteractionType(interaction.interaction_type)} · {interaction.severity}
                      </h4>

                      {interaction.matched_items.length > 0 && (
                        <p className="risk-label">
                          Matched: {interaction.matched_items.join(", ")}
                        </p>
                      )}

                      <p className="interaction-description">
                        {interaction.explanation}
                      </p>

                      <p className="interaction-description" style={{ marginTop: 10 }}>
                        <strong>Recommendation:</strong> {interaction.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {result.safe_timing_suggestions.length > 0 && (
                <>
                  <h3 className="card-title" style={{ marginTop: 28 }}>
                    Safe timing suggestions
                  </h3>
                  <ul className="action-list">
                    {result.safe_timing_suggestions.map((suggestion, index) => (
                      <li key={`${suggestion}-${index}`}>{suggestion}</li>
                    ))}
                  </ul>
                </>
              )}

              <p className="safety-panel-text" style={{ marginTop: 28 }}>
                {result.disclaimer}
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}