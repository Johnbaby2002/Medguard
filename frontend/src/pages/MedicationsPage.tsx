import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import {
  createMedication,
  deleteMedication,
  getMedications,
  type CreateMedicationPayload,
} from "../api/medications";

export default function MedicationsPage() {
  const queryClient = useQueryClient();

  const [form, setForm] = useState<CreateMedicationPayload>({
    name: "",
    dosage: "",
    frequency: "",
    medication_type: "medication",
  });

  const {
    data: medications = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["medications"],
    queryFn: getMedications,
  });

  const createMutation = useMutation({
    mutationFn: createMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["medications"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });

      setForm({
        name: "",
        dosage: "",
        frequency: "",
        medication_type: "medication",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["medications"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  function updateField(field: keyof CreateMedicationPayload, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    if (!form.name.trim() || !form.dosage.trim() || !form.frequency.trim()) {
      return;
    }

    createMutation.mutate(form);
  }

  return (
    <div>
      <div className="page-toolbar">
        <header className="page-header">
          <p className="eyebrow">Medication management</p>
          <h1 className="page-title">Medications</h1>
          <p className="page-description">
            Add and review active medications used for safety checks and reminders.
          </p>
        </header>

        <div className="summary-pill">
          <strong>{medications.length}</strong>
          total medications
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card form-card">
        <h2 className="card-title">Add medication</h2>

        <div className="form-grid">
          <label className="field">
            <span>Name</span>
            <input
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              placeholder="Ibuprofen"
            />
          </label>

          <label className="field">
            <span>Dosage</span>
            <input
              value={form.dosage}
              onChange={(event) => updateField("dosage", event.target.value)}
              placeholder="200mg"
            />
          </label>

          <label className="field">
            <span>Frequency</span>
            <input
              value={form.frequency}
              onChange={(event) => updateField("frequency", event.target.value)}
              placeholder="Once daily"
            />
          </label>

          <label className="field">
            <span>Type</span>
            <select
              value={form.medication_type}
              onChange={(event) => updateField("medication_type", event.target.value)}
            >
              <option value="medication">Medication</option>
              <option value="supplement">Supplement</option>
            </select>
          </label>
        </div>

        <button type="submit" disabled={createMutation.isPending} className="primary-button">
          <Plus size={18} />
          {createMutation.isPending ? "Adding..." : "Add medication"}
        </button>
      </form>

      {isLoading && <p className="loading-text">Loading medications...</p>}

      {error && <p className="error-text">Could not load medications.</p>}

      {!isLoading && !error && medications.length === 0 && (
        <div className="card empty-state">No medications yet.</div>
      )}

      {!isLoading && medications.length > 0 && (
        <div className="card table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Dosage</th>
                <th>Frequency</th>
                <th>Type</th>
                <th>Status</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>

            <tbody>
              {medications.map((medication) => (
                <tr key={medication.id}>
                  <td>{medication.name}</td>
                  <td>{medication.dosage}</td>
                  <td>{medication.frequency}</td>
                  <td>{medication.medication_type}</td>
                  <td>
                    <span className="badge">
                      {medication.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      type="button"
                      disabled={deleteMutation.isPending}
                      onClick={() => deleteMutation.mutate(medication.id)}
                      className="danger-button"
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}