import { useEffect, useMemo, useState } from "react";
import { Bell, CheckCircle, Trash2 } from "lucide-react";

type Reminder = {
  id: string;
  medicationName: string;
  dosage: string;
  time: string;
  frequency: string;
  notes: string;
  taken: boolean;
};

const storageKey = "medguard_reminders";

const defaultForm = {
  medicationName: "",
  dosage: "",
  time: "",
  frequency: "Daily",
  notes: "",
};

export default function RemindersPage() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [form, setForm] = useState(defaultForm);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(storageKey);

    if (stored) {
      setReminders(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(reminders));
  }, [reminders]);

  const upcomingReminders = useMemo(() => {
    return [...reminders].sort((a, b) => a.time.localeCompare(b.time));
  }, [reminders]);

  function updateForm(field: keyof typeof defaultForm, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
    setSaved(false);
  }

  function addReminder() {
    if (!form.medicationName.trim() || !form.time) {
      return;
    }

    const reminder: Reminder = {
      id: crypto.randomUUID(),
      medicationName: form.medicationName.trim(),
      dosage: form.dosage.trim(),
      time: form.time,
      frequency: form.frequency,
      notes: form.notes.trim(),
      taken: false,
    };

    setReminders((current) => [reminder, ...current]);
    setForm(defaultForm);
    setSaved(true);
  }

  function toggleTaken(id: string) {
    setReminders((current) =>
      current.map((reminder) =>
        reminder.id === id
          ? { ...reminder, taken: !reminder.taken }
          : reminder
      )
    );
  }

  function deleteReminder(id: string) {
    setReminders((current) =>
      current.filter((reminder) => reminder.id !== id)
    );
  }

  function clearAll() {
    setReminders([]);
    localStorage.removeItem(storageKey);
    setSaved(false);
  }

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Medication schedule</p>
        <h1 className="page-title">Reminders</h1>
        <p className="page-description">
          Manage medication reminders and track doses for the day.
        </p>
      </header>

      <div className="safety-layout">
        <section className="card safety-panel">
          <div className="stat-card-top">
            <div>
              <h2 className="safety-panel-title">Add reminder</h2>
              <p className="safety-panel-text">
                Create a reminder for a medication or supplement.
              </p>
            </div>

            <div className="stat-card-icon">
              <Bell size={22} />
            </div>
          </div>

          <div
            className="form-grid"
            style={{
              marginTop: 20,
              gridTemplateColumns: "1fr",
            }}
          >
            <div>
              <label>Medication name</label>
              <input
                className="input"
                placeholder="Example: Metformin"
                value={form.medicationName}
                onChange={(event) =>
                  updateForm("medicationName", event.target.value)
                }
              />
            </div>

            <div>
              <label>Dosage</label>
              <input
                className="input"
                placeholder="Example: 500 mg"
                value={form.dosage}
                onChange={(event) => updateForm("dosage", event.target.value)}
              />
            </div>

            <div>
              <label>Time</label>
              <input
                className="input"
                type="time"
                value={form.time}
                onChange={(event) => updateForm("time", event.target.value)}
              />
            </div>

            <div>
              <label>Frequency</label>
              <select
                className="input"
                value={form.frequency}
                onChange={(event) => updateForm("frequency", event.target.value)}
              >
                <option>Daily</option>
                <option>Twice daily</option>
                <option>Weekly</option>
                <option>As needed</option>
              </select>
            </div>

            <div>
              <label>Notes</label>
              <textarea
                className="input"
                rows={3}
                placeholder="Example: take with food"
                value={form.notes}
                onChange={(event) => updateForm("notes", event.target.value)}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 22 }}>
            <button className="primary-button" onClick={addReminder}>
              Add Reminder
            </button>

            <button className="secondary-button" onClick={clearAll}>
              Clear All
            </button>
          </div>

          {saved && (
            <p className="safety-panel-text" style={{ marginTop: 14 }}>
              Reminder added and saved locally.
            </p>
          )}

          {(!form.medicationName.trim() || !form.time) && (
            <p className="risk-label" style={{ marginTop: 14 }}>
              Medication name and time are required.
            </p>
          )}
        </section>

        <section className="card safety-panel">
          <h2 className="safety-panel-title">Upcoming reminders</h2>
          <p className="safety-panel-text">
            Today’s medication schedule and dose status.
          </p>

          <div className="interaction-list" style={{ marginTop: 20 }}>
            {upcomingReminders.length === 0 && (
              <div className="interaction-card">
                <h4 className="interaction-title">No reminders yet</h4>
                <p className="interaction-description">
                  Add your first reminder to start tracking medication timing.
                </p>
              </div>
            )}

            {upcomingReminders.map((reminder) => (
              <div className="interaction-card" key={reminder.id}>
                <div className="stat-card-top">
                  <div>
                    <h4 className="interaction-title">
                      {reminder.time} · {reminder.medicationName}
                    </h4>

                    <p className="risk-label">
                      {reminder.dosage || "No dosage"} · {reminder.frequency}
                    </p>
                  </div>

                  <div className="stat-card-icon">
                    <CheckCircle size={20} />
                  </div>
                </div>

                {reminder.notes && (
                  <p className="interaction-description" style={{ marginTop: 10 }}>
                    {reminder.notes}
                  </p>
                )}

                <p className="risk-label" style={{ marginTop: 12 }}>
                  Status: {reminder.taken ? "Taken" : "Not taken"}
                </p>

                <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
                  <button
                    className="secondary-button"
                    onClick={() => toggleTaken(reminder.id)}
                  >
                    {reminder.taken ? "Mark not taken" : "Mark taken"}
                  </button>

                  <button
                    className="secondary-button"
                    onClick={() => deleteReminder(reminder.id)}
                  >
                    <Trash2 size={16} /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}