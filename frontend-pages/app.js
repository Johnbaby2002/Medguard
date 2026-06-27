const API_BASE = localStorage.getItem("medguardApiBase") || "http://127.0.0.1:8000";

function token() {
  return localStorage.getItem("medguardToken") || "";
}

function setStatus(message, isError = false) {
  let target = document.querySelector("[data-status]");
  if (!target) {
    target = document.createElement("p");
    target.dataset.status = "true";
    target.className = "status-line";
    document.querySelector(".main")?.prepend(target);
  }
  target.textContent = message;
  target.style.color = isError ? "#b42318" : "#1f6f43";
}

function formJson(form) {
  const data = {};
  new FormData(form).forEach((value, key) => {
    if (value === "") return;
    if (value === "true") {
      data[key] = true;
    } else if (value === "false") {
      data[key] = false;
    } else {
      data[key] = value;
    }
  });
  return data;
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token()) {
    headers.Authorization = `Bearer ${token()}`;
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(data?.detail || `Request failed with ${response.status}`);
  }
  return data;
}

async function refreshMedications() {
  const table = document.querySelector('[data-endpoint="GET /medications"] tbody');
  if (!table || !token()) return;
  const medications = await api("/medications");
  table.innerHTML = medications.length
    ? medications
        .map(
          (med) => `
            <tr>
              <td>${med.name}</td>
              <td>${med.active_ingredient}</td>
              <td>${med.dosage}</td>
              <td><button type="button" class="secondary" data-delete-med="${med.id}">Delete</button></td>
            </tr>
          `,
        )
        .join("")
    : '<tr><td colspan="4" class="muted">No medications yet.</td></tr>';
}

async function refreshScans() {
  const table = document.querySelector("[data-scan-table] tbody");
  if (!table || !token()) return;
  const scans = await api("/scans");
  table.innerHTML = scans.length
    ? scans
        .map(
          (scan) => `
            <tr>
              <td>${scan.scan_type}</td>
              <td>${scan.medication_draft?.name || "Unknown"}</td>
              <td>${scan.status}</td>
              <td><button type="button" data-save-scan="${scan.id}">Save as medication</button></td>
            </tr>
          `,
        )
        .join("")
    : '<tr><td colspan="4" class="muted">No scan drafts yet.</td></tr>';
}

async function handleForm(form) {
  const endpoint = form.dataset.endpoint;
  if (endpoint === "POST /auth/register" || endpoint === "POST /auth/login") {
    const path = endpoint.replace("POST ", "");
    const data = await api(path, { method: "POST", body: JSON.stringify(formJson(form)) });
    localStorage.setItem("medguardToken", data.access_token);
    setStatus(`Signed in as ${data.user.email}`);
    return;
  }
  if (endpoint === "POST /medications") {
    const payload = formJson(form);
    if (!payload.name) throw new Error("Medication name is required");
    await api("/medications", { method: "POST", body: JSON.stringify(payload) });
    form.reset();
    setStatus("Medication saved");
    await refreshMedications();
    return;
  }
  if (endpoint === "POST /scans/barcode") {
    await api("/scans/barcode", { method: "POST", body: JSON.stringify(formJson(form)) });
    form.reset();
    setStatus("Barcode draft created");
    await refreshScans();
    return;
  }
  if (endpoint === "POST /scans/prescription-ocr") {
    await api("/scans/prescription-ocr", { method: "POST", body: JSON.stringify(formJson(form)) });
    form.reset();
    setStatus("OCR draft created");
    await refreshScans();
  }
}

async function handleUpload(form) {
  const body = new FormData(form);
  await api("/scans/upload", { method: "POST", body });
  form.reset();
  setStatus("Upload draft created");
  await refreshScans();
}

async function handleCamera(form) {
  const input = form.querySelector('input[type="file"]');
  const file = input?.files?.[0];
  if (!file) throw new Error("Choose or capture an image first");
  const imageData = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  await api("/scans/camera", {
    method: "POST",
    body: JSON.stringify({
      imageData,
      fileName: file.name || "camera-capture.jpg",
      contentType: file.type,
      notes: form.querySelector("[name='notes']")?.value || "",
    }),
  });
  form.reset();
  setStatus("Camera draft created");
  await refreshScans();
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  const form = button.closest("form");
  try {
    if (button.dataset.deleteMed) {
      await api(`/medications/${button.dataset.deleteMed}`, { method: "DELETE" });
      setStatus("Medication deleted");
      await refreshMedications();
    } else if (button.dataset.saveScan) {
      await api(`/scans/${button.dataset.saveScan}/medication`, { method: "POST", body: JSON.stringify({}) });
      setStatus("Scan saved as medication");
      await Promise.all([refreshScans(), refreshMedications()]);
    } else if (form?.dataset.uploadForm) {
      await handleUpload(form);
    } else if (form?.dataset.cameraForm) {
      await handleCamera(form);
    } else if (form?.dataset.endpoint) {
      await handleForm(form);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  refreshMedications().catch(() => {});
  refreshScans().catch(() => {});
});
