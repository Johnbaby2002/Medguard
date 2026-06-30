import { useEffect, useState } from "react";

type HealthProfile = {
  age: string;
  weight: string;
  sex: string;
  pregnant: string;
  kidneyDisease: string;
  liverDisease: string;
  allergies: string;
  conditions: string;
  notes: string;
};

const emptyProfile: HealthProfile = {
  age: "",
  weight: "",
  sex: "Not specified",
  pregnant: "No",
  kidneyDisease: "No",
  liverDisease: "No",
  allergies: "",
  conditions: "",
  notes: "",
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<HealthProfile>(emptyProfile);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("medguard_health_profile");

    if (stored) {
      setProfile(JSON.parse(stored));
    }
  }, []);

  function updateField(field: keyof HealthProfile, value: string) {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));

    setSaved(false);
  }

  function saveProfile() {
    localStorage.setItem("medguard_health_profile", JSON.stringify(profile));
    setSaved(true);
  }

  function resetProfile() {
    setProfile(emptyProfile);
    localStorage.removeItem("medguard_health_profile");
    setSaved(false);
  }

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Health data</p>
        <h1 className="page-title">Health Profile</h1>
        <p className="page-description">
          Basic health information used by MedGuard during safety analysis.
        </p>
      </header>

      <div className="safety-layout">
        <section className="card safety-panel">
          <h2 className="safety-panel-title">Personal details</h2>
          <p className="safety-panel-text">
            Add health details that may affect medication safety checks.
          </p>

          <div 
          className="form-grid"
          style={{marginTop: 20,
            gridTemplateColumns: "1fr",
            }}
>
            <div>
              <label>Age</label>
              <input
                className="input"
                type="number"
                placeholder="Example: 42"
                value={profile.age}
                onChange={(event) => updateField("age", event.target.value)}
              />
            </div>

            <div>
              <label>Weight (kg)</label>
              <input
                className="input"
                type="number"
                placeholder="Example: 75"
                value={profile.weight}
                onChange={(event) => updateField("weight", event.target.value)}
              />
            </div>

            <div>
              <label>Sex</label>
              <select
                className="input"
                value={profile.sex}
                onChange={(event) => updateField("sex", event.target.value)}
              >
                <option>Not specified</option>
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
              </select>
            </div>

            <div>
              <label>Pregnant</label>
              <select
                className="input"
                value={profile.pregnant}
                onChange={(event) => updateField("pregnant", event.target.value)}
              >
                <option>No</option>
                <option>Yes</option>
                <option>Not applicable</option>
              </select>
            </div>

            <div>
              <label>Kidney disease</label>
              <select
                className="input"
                value={profile.kidneyDisease}
                onChange={(event) =>
                  updateField("kidneyDisease", event.target.value)
                }
              >
                <option>No</option>
                <option>Yes</option>
                <option>Unknown</option>
              </select>
            </div>

            <div>
              <label>Liver disease</label>
              <select
                className="input"
                value={profile.liverDisease}
                onChange={(event) =>
                  updateField("liverDisease", event.target.value)
                }
              >
                <option>No</option>
                <option>Yes</option>
                <option>Unknown</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 20 }}>
            <label>Allergies</label>
            <textarea
              className="input"
              rows={3}
              placeholder="Example: penicillin, aspirin"
              value={profile.allergies}
              onChange={(event) => updateField("allergies", event.target.value)}
            />
          </div>

          <div style={{ marginTop: 16 }}>
            <label>Medical conditions</label>
            <textarea
              className="input"
              rows={3}
              placeholder="Example: hypertension, diabetes"
              value={profile.conditions}
              onChange={(event) => updateField("conditions", event.target.value)}
            />
          </div>

          <div style={{ marginTop: 16 }}>
            <label>Notes</label>
            <textarea
              className="input"
              rows={3}
              placeholder="Anything else MedGuard should consider"
              value={profile.notes}
              onChange={(event) => updateField("notes", event.target.value)}
            />
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 22 }}>
            <button className="primary-button" onClick={saveProfile}>
              Save Profile
            </button>

            <button className="secondary-button" onClick={resetProfile}>
              Reset
            </button>
          </div>

          {saved && (
            <p className="safety-panel-text" style={{ marginTop: 14 }}>
              Profile saved locally.
            </p>
          )}
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Profile summary</h2>
          <p className="safety-panel-text">
            Current saved health context preview.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            <div className="interaction-card">
              <h4 className="interaction-title">Basic info</h4>
              <p className="risk-label">Age: {profile.age || "Not set"}</p>
              <p className="risk-label">
                Weight: {profile.weight ? `${profile.weight} kg` : "Not set"}
              </p>
              <p className="risk-label">Sex: {profile.sex}</p>
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Risk factors</h4>
              <p className="risk-label">Pregnant: {profile.pregnant}</p>
              <p className="risk-label">
                Kidney disease: {profile.kidneyDisease}
              </p>
              <p className="risk-label">Liver disease: {profile.liverDisease}</p>
            </div>

            <div className="interaction-card">
              <h4 className="interaction-title">Clinical notes</h4>
              <p className="interaction-description">
                <strong>Allergies:</strong> {profile.allergies || "None added"}
              </p>
              <p className="interaction-description" style={{ marginTop: 8 }}>
                <strong>Conditions:</strong>{" "}
                {profile.conditions || "None added"}
              </p>
              <p className="interaction-description" style={{ marginTop: 8 }}>
                <strong>Notes:</strong> {profile.notes || "None added"}
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}