import { useEffect, useMemo, useState } from "react";

interface Substance {
  id: string;
  name: string;
  type: string;
  amount: string;
  frequency: string;
  notes: string;
}

const storageKey = "medguard_substances";

const defaultSubstance: Omit<Substance, "id"> = {
  name: "",
  type: "Lifestyle",
  amount: "",
  frequency: "",
  notes: "",
};

export default function SubstancesPage() {
  const [substances, setSubstances] = useState<Substance[]>([]);
  const [form, setForm] = useState(defaultSubstance);

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      setSubstances(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(substances));
  }, [substances]);

  const stats = useMemo(() => {
    const dailyCount = substances.filter((item) =>
      item.frequency.toLowerCase().includes("daily")
    ).length;

    const typesCount = new Set(substances.map((item) => item.type)).size;

    return {
      total: substances.length,
      daily: dailyCount,
      types: typesCount,
    };
  }, [substances]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) return;

    const newSubstance: Substance = {
      id: crypto.randomUUID(),
      ...form,
      name: form.name.trim(),
    };

    setSubstances((current) => [newSubstance, ...current]);
    setForm(defaultSubstance);
  }

  function deleteSubstance(id: string) {
    setSubstances((current) => current.filter((item) => item.id !== id));
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Lifestyle safety assistant</p>
          <h1 className="page-title">Substances</h1>
          <p className="page-description">
            Track alcohol, caffeine, nicotine, grapefruit, OTC medicines, and
            other substances that may affect medication safety.
          </p>
        </div>
      </header>

      <section className="stats-grid">
        <article className="stat-card">
          <div className="stat-card-top">
            <span className="stat-card-title">Total substances</span>
            <span className="stat-card-icon">🧪</span>
          </div>
          <strong className="stat-card-value">{stats.total}</strong>
        </article>

        <article className="stat-card">
          <div className="stat-card-top">
            <span className="stat-card-title">Daily use</span>
            <span className="stat-card-icon">📅</span>
          </div>
          <strong className="stat-card-value">{stats.daily}</strong>
        </article>

        <article className="stat-card">
          <div className="stat-card-top">
            <span className="stat-card-title">Types</span>
            <span className="stat-card-icon">🏷️</span>
          </div>
          <strong className="stat-card-value">{stats.types}</strong>
        </article>
      </section>

      <section className="form-card">
        <div className="card-title">Add substance</div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Name
              <input
                className="input"
                value={form.name}
                onChange={(event) =>
                  setForm({ ...form, name: event.target.value })
                }
                placeholder="Alcohol, coffee, grapefruit juice..."
              />
            </label>

            <label>
              Type
              <select
                className="input"
                value={form.type}
                onChange={(event) =>
                  setForm({ ...form, type: event.target.value })
                }
              >
                <option>Lifestyle</option>
                <option>Food / Drink</option>
                <option>OTC Medicine</option>
                <option>Recreational</option>
                <option>Other</option>
              </select>
            </label>

            <label>
              Amount
              <input
                className="input"
                value={form.amount}
                onChange={(event) =>
                  setForm({ ...form, amount: event.target.value })
                }
                placeholder="2 cups, 1 glass, 200mg..."
              />
            </label>

            <label>
              Frequency
              <input
                className="input"
                value={form.frequency}
                onChange={(event) =>
                  setForm({ ...form, frequency: event.target.value })
                }
                placeholder="Daily, weekly, occasionally..."
              />
            </label>
          </div>

          <label>
            Notes
            <textarea
              className="input"
              value={form.notes}
              onChange={(event) =>
                setForm({ ...form, notes: event.target.value })
              }
              placeholder="Timing, habits, warnings, personal observations..."
              rows={4}
            />
          </label>

          <button className="primary-button" type="submit">
            Add substance
          </button>
        </form>
      </section>

      <section className="table-card">
        <div className="card-title">Saved substances</div>

        {substances.length === 0 ? (
          <p className="page-description">
            No substances added yet. Add one above to start tracking lifestyle
            and interaction risks.
          </p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Frequency</th>
                <th>Notes</th>
                <th />
              </tr>
            </thead>

            <tbody>
              {substances.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>
                    <span className="badge">{item.type}</span>
                  </td>
                  <td>{item.amount || "—"}</td>
                  <td>{item.frequency || "—"}</td>
                  <td>{item.notes || "—"}</td>
                  <td>
                    <button
                      className="danger-button"
                      type="button"
                      onClick={() => deleteSubstance(item.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}