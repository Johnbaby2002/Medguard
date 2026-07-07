import { useEffect, useMemo, useState } from "react";

interface Supplement {
  id: string;
  name: string;
  category: string;
  dose: string;
  frequency: string;
  notes: string;
}

const storageKey = "medguard_supplements";

const emptyForm = {
  name: "",
  category: "",
  dose: "",
  frequency: "",
  notes: "",
};

export default function SupplementsPage() {
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);

    if (saved) {
      setSupplements(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(supplements));
  }, [supplements]);

  const dailyCount = useMemo(() => {
    return supplements.filter((item) =>
      item.frequency.toLowerCase().includes("daily")
    ).length;
  }, [supplements]);

  const categoryCount = useMemo(() => {
    return new Set(
      supplements
        .map((item) => item.category.trim().toLowerCase())
        .filter(Boolean)
    ).size;
  }, [supplements]);

  function addSupplement() {
    if (!form.name.trim()) return;

    const newSupplement: Supplement = {
      id: crypto.randomUUID(),
      name: form.name.trim(),
      category: form.category.trim(),
      dose: form.dose.trim(),
      frequency: form.frequency.trim(),
      notes: form.notes.trim(),
    };

    setSupplements((prev) => [newSupplement, ...prev]);
    setForm(emptyForm);
  }

  function deleteSupplement(id: string) {
    setSupplements((prev) => prev.filter((item) => item.id !== id));
  }

  return (
    <div>
      <header className="page-header">
        <p className="eyebrow">Medication safety assistant</p>
        <h1 className="page-title">Supplements</h1>
        <p className="page-description">
          Track vitamins, minerals, herbal products, and workout supplements
          that may affect medication safety.
        </p>
      </header>

      <section className="stats-grid" style={{ marginBottom: 28 }}>
        <article className="card stat-card">
          <div className="stat-card-top">
            <p className="stat-card-title">Total supplements</p>
            <span className="stat-card-icon">💊</span>
          </div>
          <p className="stat-card-value">{supplements.length}</p>
        </article>

        <article className="card stat-card">
          <div className="stat-card-top">
            <p className="stat-card-title">Daily items</p>
            <span className="stat-card-icon">📅</span>
          </div>
          <p className="stat-card-value">{dailyCount}</p>
        </article>

        <article className="card stat-card">
          <div className="stat-card-top">
            <p className="stat-card-title">Categories</p>
            <span className="stat-card-icon">🏷️</span>
          </div>
          <p className="stat-card-value">{categoryCount}</p>
        </article>
      </section>

      <section className="card form-card">
        <h2 className="card-title">Add supplement</h2>

        <div className="form-grid">
          <label>
            Name
            <input
              className="input"
              placeholder="Vitamin D"
              value={form.name}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, name: e.target.value }))
              }
            />
          </label>

          <label>
            Category
            <input
              className="input"
              placeholder="Vitamin, mineral, herbal, workout"
              value={form.category}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, category: e.target.value }))
              }
            />
          </label>

          <label>
            Dose
            <input
              className="input"
              placeholder="2000 IU, 500mg, 5g"
              value={form.dose}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, dose: e.target.value }))
              }
            />
          </label>

          <label>
            Frequency
            <input
              className="input"
              placeholder="daily, weekly, before workout"
              value={form.frequency}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, frequency: e.target.value }))
              }
            />
          </label>
        </div>

        <label style={{ display: "block", marginTop: 16 }}>
          <span
            style={{
              display: "block",
              marginBottom: 8,
              color: "#9ca3af",
              fontSize: 14,
            }}
          >
            Notes
          </span>
          <textarea
            className="input"
            placeholder="Brand, reason for taking it, warnings, or anything important"
            value={form.notes}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, notes: e.target.value }))
            }
          />
        </label>

        <button
          className="primary-button"
          type="button"
          onClick={addSupplement}
          disabled={!form.name.trim()}
        >
          Add Supplement
        </button>
      </section>

      <section className="card table-card">
        <div
          style={{
            padding: "22px 24px",
            borderBottom: "1px solid #1e293b",
          }}
        >
          <h2 className="card-title" style={{ marginBottom: 6 }}>
            Saved supplements
          </h2>
          <p style={{ margin: 0, color: "#94a3b8" }}>
            These items are stored locally for now and can later be used in
            safety checks. Потому что, конечно, магний тоже решил участвовать в драме.
          </p>
        </div>

        {supplements.length === 0 ? (
          <div className="empty-state">
            No supplements added yet. Add one above to start tracking.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Dose</th>
                <th>Frequency</th>
                <th>Notes</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {supplements.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>
                    {item.category ? (
                      <span className="badge">{item.category}</span>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td>{item.dose || "-"}</td>
                  <td>{item.frequency || "-"}</td>
                  <td>{item.notes || "-"}</td>
                  <td>
                    <button
                      className="danger-button"
                      type="button"
                      onClick={() => deleteSupplement(item.id)}
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