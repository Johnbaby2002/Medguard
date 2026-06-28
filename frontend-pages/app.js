const API_CANDIDATES = [
  localStorage.getItem("medguardApiBase"),
  "http://127.0.0.1:8000",
  "http://127.0.0.1:8001",
  "http://127.0.0.1:8002",
  "http://127.0.0.1:8003",
].filter(Boolean);

let API_BASE = API_CANDIDATES[0];

function token() {
  return localStorage.getItem("medguardToken") || sessionStorage.getItem("medguardToken") || "";
}

function clearToken() {
  localStorage.removeItem("medguardToken");
  sessionStorage.removeItem("medguardToken");
}

function isAuthEndpoint(endpoint = "") {
  return endpoint.startsWith("POST /auth/");
}

function currentPageName() {
  return window.location.pathname.split("/").pop() || "index.html";
}

function requireLogin() {
  if (token()) return true;
  setStatus("Please login first. Opening login...", true);
  window.setTimeout(() => {
    window.location.href = `login.html?next=${encodeURIComponent(currentPageName() + window.location.search)}`;
  }, 700);
  return false;
}

function setStatus(message, isError = false) {
  let target = document.querySelector("[data-status]");
  if (!target) {
    target = document.createElement("p");
    target.dataset.status = "true";
    target.className = "status-line";
    const statusHost = document.querySelector(".main") || document.querySelector(".auth-panel") || document.body;
    statusHost.prepend(target);
  }
  target.textContent = message;
  target.classList.remove("hidden");
  target.classList.toggle("error", isError);
  target.classList.toggle("success", !isError);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function asList(value) {
  if (Array.isArray(value)) return value;
  if (!value) return [];
  return String(value)
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function listHtml(items, emptyText = "None listed") {
  const cleanItems = items.filter((item) => item !== undefined && item !== null && item !== "");
  if (!cleanItems.length) return `<p class="muted">${emptyText}</p>`;
  return `<ul class="plain-list">${cleanItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function formatApiError(data, fallback) {
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((item) => item.msg || item.message || JSON.stringify(item))
      .join(" ");
  }
  return fallback;
}

function formJson(form) {
  const data = {};
  Array.from(form.elements).forEach((element) => {
    if (!element.name || element.disabled) return;
    if (element.type === "checkbox") {
      data[element.name] = element.checked;
    }
  });
  new FormData(form).forEach((value, key) => {
    if (value === "") return;
    if (value === "on") {
      data[key] = true;
    } else if (value === "true") {
      data[key] = true;
    } else if (value === "false") {
      data[key] = false;
    } else {
      data[key] = value;
    }
  });
  return data;
}

function profilePayload(form) {
  const payload = formJson(form);
  payload.knownConditions = asList(payload.knownConditions);
  payload.allergies = asList(payload.allergies);
  return payload;
}

function storeToken(accessToken, remember = true) {
  localStorage.removeItem("medguardToken");
  sessionStorage.removeItem("medguardToken");
  const store = remember ? localStorage : sessionStorage;
  store.setItem("medguardToken", accessToken);
}

async function api(path, options = {}) {
  if (!token() && !path.startsWith("/auth/")) {
    throw new Error("Please login first.");
  }
  const headers = options.headers || {};
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token()) {
    headers.Authorization = `Bearer ${token()}`;
  }
  let lastNetworkError = null;
  let lastResponseError = null;
  for (let index = 0; index < API_CANDIDATES.length; index += 1) {
    const baseUrl = API_CANDIDATES[index];
    try {
      const response = await fetch(`${baseUrl}${path}`, { ...options, headers });
      const text = await response.text();
      const data = text ? JSON.parse(text) : null;
      if (!response.ok) {
        if ([401, 403].includes(response.status) && !path.startsWith("/auth/")) {
          clearToken();
          throw new Error("Please login first.");
        }
        if ([404, 405].includes(response.status) && index < API_CANDIDATES.length - 1) {
          lastResponseError = new Error(formatApiError(data, `Request failed with ${response.status}`));
          continue;
        }
        throw new Error(formatApiError(data, `Request failed with ${response.status}`));
      }
      API_BASE = baseUrl;
      localStorage.setItem("medguardApiBase", baseUrl);
      return data;
    } catch (error) {
      if (error instanceof TypeError) {
        lastNetworkError = error;
        continue;
      }
      throw error;
    }
  }
  if (lastResponseError) throw lastResponseError;
  throw new Error(
    `Cannot reach the MedGuard backend. Start it on http://127.0.0.1:8000, 8001, 8002, or 8003. ${lastNetworkError?.message || ""}`.trim(),
  );
}

function setButtonLoading(button, loading) {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = "Please wait...";
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

async function showCurrentUser() {
  if (!token() || document.body.classList.contains("auth-page")) return;
  try {
    const user = await api("/auth/me");
    let userBox = document.querySelector("[data-user-box]");
    if (!userBox) {
      userBox = document.createElement("div");
      userBox.dataset.userBox = "true";
      userBox.className = "user-box";
      document.querySelector(".topbar")?.append(userBox);
    }
    userBox.innerHTML = `<span>${user.full_name}</span><button type="button" class="secondary tiny" data-logout>Logout</button>`;
  } catch {
    localStorage.removeItem("medguardToken");
    sessionStorage.removeItem("medguardToken");
  }
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

async function refreshSubstances() {
  const table = document.querySelector('[data-endpoint="GET /substances"] tbody');
  if (!table || !token()) return;
  const substances = await api("/substances");
  table.innerHTML = substances.length
    ? substances
        .map(
          (item) => `
            <tr>
              <td>${escapeHtml(item.name)}</td>
              <td>${escapeHtml(item.category)}</td>
              <td>${escapeHtml(item.active_ingredient || "")}</td>
              <td>${item.is_active ? "Active" : "Inactive"}</td>
              <td><button type="button" class="secondary" data-delete-substance="${item.id}">Delete</button></td>
            </tr>
          `,
        )
        .join("")
    : '<tr><td colspan="5" class="muted">No substances or lifestyle factors saved yet.</td></tr>';
}

async function renderDashboardSummary() {
  const container = document.querySelector("[data-dashboard-summary]");
  if (!container || !token()) return;
  const summary = await api("/dashboard/summary");
  container.querySelector("[data-total-medications]").textContent = summary.total_medications;
  container.querySelector("[data-active-reminders]").textContent = summary.active_reminders_today;
  container.querySelector("[data-highest-risk]").textContent = summary.highest_current_risk_level;
  container.querySelector("[data-supplements]").textContent = summary.total_supplements;
  container.querySelector("[data-interactions]").textContent = summary.detected_interactions;
  container.querySelector("[data-missed-doses]").textContent = summary.missed_doses_today;
  container.querySelector("[data-adherence]").textContent =
    summary.adherence_percentage === null ? "No logs yet" : `${summary.adherence_percentage}%`;
  container.querySelector("[data-next-reminder]").textContent = summary.next_medication_reminder
    ? `${summary.next_medication_reminder.time} - ${summary.next_medication_reminder.medication_name || "Medication"}`
    : "No reminder scheduled";
}

async function renderRiskSummary() {
  const container = document.querySelector("[data-risk-summary]");
  if (!container || !token()) return;
  const summary = await api("/dashboard/risk-summary");
  container.querySelector("[data-risk-score]").textContent = summary.risk_score_0_to_100;
  container.querySelector("[data-risk-level]").textContent = summary.highest_risk_level;
  container.querySelector("[data-risk-level]").className = `badge severity-${summary.highest_risk_level}`;
  container.querySelector("[data-risk-missed]").textContent = summary.missed_doses_today;
  container.querySelector("[data-risk-adherence]").textContent =
    summary.adherence_percentage === null ? "No schedule" : `${summary.adherence_percentage}%`;
  container.querySelector("[data-risk-next]").textContent = summary.next_reminder
    ? `${summary.next_reminder.time} - ${summary.next_reminder.medication_name || "Medication"}`
    : "No pending reminder";
  container.querySelector("[data-risk-warnings]").innerHTML = listHtml(
    summary.top_3_warnings.map((warning) => `${warning.severity}: ${warning.explanation}`),
    "No active warnings detected.",
  );
}

function timelineBucketHtml(title, items) {
  return `
    <article class="card">
      <h2>${title}</h2>
      ${
        items.length
          ? `<table class="table"><thead><tr><th>Time</th><th>Medication</th><th>Dose</th><th>Status</th></tr></thead><tbody>${items
              .map(
                (item) => `
                  <tr>
                    <td>${escapeHtml(item.time)}</td>
                    <td>${escapeHtml(item.medication_name)}</td>
                    <td>${escapeHtml(item.dose)}</td>
                    <td><span class="badge">${escapeHtml(item.status)}</span></td>
                  </tr>
                `,
              )
              .join("")}</tbody></table>`
          : '<p class="muted">No scheduled doses.</p>'
      }
    </article>
  `;
}

async function renderTimeline() {
  const target = document.querySelector("[data-timeline]");
  if (!target || !token()) return;
  const timeline = await api("/timeline/today");
  target.innerHTML = [
    timelineBucketHtml("Morning", timeline.morning),
    timelineBucketHtml("Afternoon", timeline.afternoon),
    timelineBucketHtml("Evening", timeline.evening),
    timelineBucketHtml("Night", timeline.night),
  ].join("");
}

async function renderAdherence() {
  const target = document.querySelector("[data-adherence-summary]");
  if (!target || !token()) return;
  const summary = await api("/adherence/summary");
  target.innerHTML = `
    <article class="card">
      <h2>Adherence</h2>
      <div class="metric">${escapeHtml(summary.adherence_percentage ?? "No schedule")}${summary.adherence_percentage === null ? "" : "%"}</div>
      <p class="muted">${summary.taken_doses} taken, ${summary.late_doses} late, ${summary.missed_doses} missed</p>
    </article>
    <article class="card">
      <h2>Weekly trend</h2>
      <table class="table">
        <thead><tr><th>Date</th><th>Scheduled</th><th>Taken</th><th>Late</th><th>Missed</th><th>%</th></tr></thead>
        <tbody>${summary.weekly_trend
          .map(
            (day) => `
              <tr>
                <td>${escapeHtml(day.date)}</td>
                <td>${escapeHtml(day.scheduled)}</td>
                <td>${escapeHtml(day.taken)}</td>
                <td>${escapeHtml(day.late)}</td>
                <td>${escapeHtml(day.missed)}</td>
                <td>${escapeHtml(day.adherence_percentage ?? "-")}</td>
              </tr>
            `,
          )
          .join("")}</tbody>
      </table>
    </article>
  `;
}

async function refreshSideEffects() {
  const table = document.querySelector('[data-endpoint="GET /side-effects"] tbody');
  if (!table || !token()) return;
  const logs = await api("/side-effects");
  table.innerHTML = logs.length
    ? logs
        .map(
          (log) => `
            <tr>
              <td>${escapeHtml(log.symptom)}</td>
              <td>${escapeHtml(log.severity)}</td>
              <td>${new Date(log.started_at).toLocaleString()}</td>
              <td>${escapeHtml(log.notes || "")}</td>
            </tr>
          `,
        )
        .join("")
    : '<tr><td colspan="4" class="muted">No side effect logs yet.</td></tr>';
}

async function renderSideEffectSummary() {
  const target = document.querySelector("[data-side-effect-summary]");
  if (!target || !token()) return;
  const summary = await api("/side-effects/summary");
  target.innerHTML = `
    <p class="muted">${escapeHtml(summary.note)}</p>
    ${listHtml(summary.grouped_symptoms.map((item) => `${item.symptom}: ${item.frequency} time(s)`), "No symptoms logged.")}
  `;
}

async function renderSafetyCheck() {
  const target = document.querySelector("[data-safety-result]");
  if (!target) return;
  const result = await api("/safety-check", { method: "POST", body: JSON.stringify({}) });
  target.innerHTML = `
    <article class="card warning">
      <h2>Risk summary</h2>
      <p><strong>Total risk score:</strong> ${escapeHtml(result.total_risk_score)}</p>
      <p><strong>Highest severity:</strong> ${escapeHtml(result.highest_severity)}</p>
      <p class="muted">${escapeHtml(result.disclaimer)}</p>
    </article>
    <article class="card">
      <h2>Recommended actions</h2>
      ${listHtml(result.recommended_actions)}
    </article>
  `;
  const historyTable = document.querySelector('[data-endpoint="GET /interactions/history"] tbody');
  if (historyTable) await renderInteractionHistory(historyTable);
}

async function renderInteractionHistory(table) {
  const history = await api("/interactions/history");
  table.innerHTML = history.length
    ? history
        .map(
          (row) => `
            <tr>
              <td>${new Date(row.created_at).toLocaleString()}</td>
              <td>${escapeHtml(row.highest_severity)}</td>
              <td>${escapeHtml(row.total_risk_score)}</td>
              <td>${escapeHtml(row.interactions?.length || 0)} interactions</td>
            </tr>
          `,
        )
        .join("")
    : '<tr><td colspan="4" class="muted">No saved safety checks yet.</td></tr>';
}

async function renderEmergencyCard() {
  const target = document.querySelector("[data-emergency-card]");
  if (!target) return;
  const card = await api("/emergency-card");
  const warnings = card.highest_risk_warnings.map(
    (warning) => `${warning.severity}: ${warning.explanation} ${warning.recommendation}`,
  );
  target.innerHTML = `
    <article class="card emergency-card print-card">
      <div class="emergency-head">
        <div>
          <p class="eyebrow">For emergency use</p>
          <h2>${escapeHtml(card.full_name || card.user_name)}</h2>
          <p>Age: ${escapeHtml(card.age ?? "Not listed")}</p>
          <p>Generated: ${new Date(card.generated_date || card.generated_at).toLocaleString()}</p>
        </div>
        <div class="qr-box">${escapeHtml(card.qr_code_placeholder)}</div>
      </div>
      <section class="grid two">
        <div>
          <h3>Allergies</h3>
          ${listHtml(card.allergies)}
        </div>
        <div>
          <h3>Known conditions</h3>
          ${listHtml(card.conditions)}
        </div>
        <div>
          <h3>Current medications</h3>
          ${listHtml(card.current_medications.map((med) => `${med.name} - ${med.dosage} - ${med.frequency}`))}
        </div>
        <div>
          <h3>Emergency contact</h3>
          ${listHtml([
            card.emergency_contact?.name,
            card.emergency_contact?.phone,
            card.emergency_contact?.email,
          ])}
        </div>
        <div>
          <h3>Substances & lifestyle risks</h3>
          ${listHtml((card.substances_lifestyle_risks || []).map((item) => `${item.name} - ${item.category}`), "None listed")}
        </div>
      </section>
      <h3>Highest risk warnings</h3>
      ${listHtml(warnings, "No high or critical warnings detected.")}
      <p class="muted">${escapeHtml(card.disclaimer)}</p>
    </article>
  `;
}

async function renderMedicationReport() {
  const target = document.querySelector("[data-report]");
  if (!target) return;
  const report = await api("/reports/medication-summary");
  target.innerHTML = `
    <article class="card">
      <h2>Profile summary</h2>
      <pre>${escapeHtml(JSON.stringify(report.user_profile_summary, null, 2))}</pre>
    </article>
    <article class="card warning">
      <h2>Detected risks</h2>
      <p><strong>${escapeHtml(report.detected_risks.highest_severity)}</strong> risk, score ${escapeHtml(report.detected_risks.total_risk_score)}</p>
      ${listHtml(report.detected_risks.interactions.map((item) => `${item.severity}: ${item.explanation}`))}
    </article>
    <article class="card">
      <h2>Current medications</h2>
      ${listHtml(report.current_medications.map((med) => `${med.name} - ${med.dosage} - ${med.frequency}`))}
    </article>
    <article class="card">
      <h2>Adherence</h2>
      <p>Adherence: ${escapeHtml(report.adherence_summary.adherence_percentage ?? "No logs yet")}</p>
      <p>Missed doses: ${escapeHtml(report.missed_doses.length)}</p>
      ${listHtml(report.recommendations)}
    </article>
  `;
}

async function handleForm(form) {
  const endpoint = form.dataset.endpoint;
  if (endpoint === "POST /auth/register") {
    const payload = formJson(form);
    if (payload.password !== payload.repeatPassword) {
      throw new Error("Passwords do not match");
    }
    if (!/[A-Z]/.test(payload.password) || !/[a-z]/.test(payload.password) || !/[^A-Za-z0-9]/.test(payload.password)) {
      throw new Error("Password needs uppercase, lowercase, and a special character, for example Medguard99!");
    }
    if (!payload.termsConsent) throw new Error("Terms and privacy consent is required");
    if (!payload.medicalDisclaimerConsent) throw new Error("Medical disclaimer consent is required");
    const data = await api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
    clearToken();
    form.reset();
    setStatus(`Account created for ${data.user.full_name}. Opening login...`);
    window.setTimeout(() => {
      window.location.href = `login.html?registered=${encodeURIComponent(data.user.email)}`;
    }, 900);
    return;
  }
  if (endpoint === "PUT /profile") {
    const data = await api("/profile", { method: "PUT", body: JSON.stringify(profilePayload(form)) });
    setStatus(`Profile saved for age ${data.age ?? "not set"}`);
    return;
  }
  if (endpoint === "POST /caregiver/invite") {
    await api("/caregiver/invite", { method: "POST", body: JSON.stringify(formJson(form)) });
    form.reset();
    setStatus("Caregiver invite saved");
    return;
  }
  if (endpoint === "POST /substances") {
    await api("/substances", { method: "POST", body: JSON.stringify(formJson(form)) });
    form.reset();
    setStatus("Substance or lifestyle factor saved");
    await refreshSubstances();
    return;
  }
  if (endpoint === "POST /side-effects") {
    await api("/side-effects", { method: "POST", body: JSON.stringify(formJson(form)) });
    form.reset();
    setStatus("Side effect log saved");
    await Promise.all([refreshSideEffects(), renderSideEffectSummary()]);
    return;
  }
  if (endpoint === "POST /assistant/ask") {
    const result = await api("/assistant/ask", { method: "POST", body: JSON.stringify(formJson(form)) });
    document.querySelector("[data-assistant-answer]").innerHTML = `
      <article class="card">
        <h2>Answer</h2>
        <p>${escapeHtml(result.answer)}</p>
        <h2>Recommendation</h2>
        <p>${escapeHtml(result.recommendation)}</p>
        ${listHtml(result.related_interactions.map((item) => `${item.severity}: ${item.explanation}`), "No related interactions found.")}
        <p class="muted">${escapeHtml(result.disclaimer)}</p>
      </article>
    `;
    return;
  }
  if (endpoint === "POST /share/report-link") {
    const result = await api("/share/report-link", { method: "POST", body: JSON.stringify(formJson(form)) });
    document.querySelector("[data-share-result]").innerHTML = `
      <p><strong>Share path:</strong> ${escapeHtml(result.url_path)}</p>
      <p><strong>Expires:</strong> ${new Date(result.expires_at).toLocaleString()}</p>
    `;
    setStatus("Share link created");
    return;
  }
  if (endpoint === "POST /auth/login") {
    const payload = formJson(form);
    const data = await api("/auth/login", { method: "POST", body: JSON.stringify(payload) });
    storeToken(data.access_token, Boolean(payload.rememberMe));
    setStatus(`Signed in as ${data.user.full_name}`);
    window.setTimeout(() => {
      window.location.href = new URLSearchParams(window.location.search).get("next") || "index.html";
    }, 400);
    return;
  }
  if (endpoint === "POST /auth/forgot-password") {
    const data = await api("/auth/forgot-password", { method: "POST", body: JSON.stringify(formJson(form)) });
    setStatus(data.reset_token ? `Reset token: ${data.reset_token}` : data.message);
    return;
  }
  if (endpoint === "POST /auth/reset-password") {
    const payload = formJson(form);
    if (payload.password !== payload.repeatPassword) {
      throw new Error("Passwords do not match");
    }
    const data = await api("/auth/reset-password", { method: "POST", body: JSON.stringify(payload) });
    storeToken(data.access_token, true);
    form.reset();
    setStatus(`Password reset. Signed in as ${data.user.email}`);
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

async function handleMedicationUpload(form) {
  const body = new FormData(form);
  if (!body.get("file")?.name) throw new Error("Choose an image or PDF first");
  await api("/medications/upload", { method: "POST", body });
  form.reset();
  setStatus("Medication added from upload");
  await refreshMedications();
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

async function handleMedicationCamera(form) {
  const input = form.querySelector('input[type="file"]');
  const file = input?.files?.[0];
  if (!file) throw new Error("Choose or capture an image first");
  const imageData = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  await api("/medications/camera", {
    method: "POST",
    body: JSON.stringify({
      imageData,
      fileName: file.name || "camera-capture.jpg",
      contentType: file.type,
      name: form.querySelector("[name='name']")?.value || "",
      ocrText: form.querySelector("[name='ocrText']")?.value || "",
      dosage: form.querySelector("[name='dosage']")?.value || "",
      frequency: form.querySelector("[name='frequency']")?.value || "",
    }),
  });
  form.reset();
  setStatus("Medication added from camera");
  await refreshMedications();
}

async function renderAssistantStatus() {
  const target = document.querySelector("[data-assistant-status]");
  if (!target || !getToken()) return;
  const status = await api("/assistant/status");
  const badge = status.connected ? "success" : "warning";
  target.innerHTML = `
    <h2>Assistant connection</h2>
    <p><span class="badge ${badge}">${status.connected ? "Local AI connected" : "Rule-based fallback"}</span></p>
    <p>${escapeHtml(status.message || "")}</p>
    <p class="muted">Module: ${escapeHtml(status.module || "not configured")}</p>
  `;
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  if (button.dataset.togglePassword !== undefined) {
    const input = button.closest(".password-row")?.querySelector("input");
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
    button.textContent = input.type === "password" ? "Show" : "Hide";
    return;
  }
  if (button.dataset.authTab) {
    document.querySelectorAll("[data-auth-tab]").forEach((tab) => tab.classList.toggle("active", tab === button));
    document.querySelectorAll("[data-auth-section]").forEach((section) => {
      section.classList.toggle("hidden", section.dataset.authSection !== button.dataset.authTab);
    });
    return;
  }
  if (button.dataset.logout !== undefined) {
    clearToken();
    window.location.href = "login.html";
    return;
  }
  const form = button.closest("form");
  const endpoint = form?.dataset.endpoint || button.dataset.endpoint || "";
  const protectedAction =
    button.dataset.deleteMed ||
    button.dataset.deleteSubstance ||
    button.dataset.saveScan ||
    button.dataset.substancePreset ||
    form?.dataset.medUploadForm ||
    form?.dataset.medCameraForm ||
    form?.dataset.uploadForm ||
    form?.dataset.cameraForm ||
    (endpoint && !isAuthEndpoint(endpoint));
  if (protectedAction && !requireLogin()) return;
  try {
    setButtonLoading(button, true);
    if (button.dataset.endpoint === "GET /emergency-card") {
      await renderEmergencyCard();
      setStatus("Emergency card loaded");
    } else if (button.dataset.endpoint === "GET /reports/medication-summary") {
      await renderMedicationReport();
      setStatus("Medication summary generated");
    } else if (button.dataset.endpoint === "POST /safety-check") {
      await renderSafetyCheck();
      setStatus("Safety check completed");
    } else if (button.dataset.deleteMed) {
      await api(`/medications/${button.dataset.deleteMed}`, { method: "DELETE" });
      setStatus("Medication deleted");
      await refreshMedications();
    } else if (button.dataset.deleteSubstance) {
      await api(`/substances/${button.dataset.deleteSubstance}`, { method: "DELETE" });
      setStatus("Substance or lifestyle factor deleted");
      await refreshSubstances();
    } else if (button.dataset.substancePreset) {
      await api("/substances", { method: "POST", body: button.dataset.substancePreset });
      setStatus("Quick item saved");
      await refreshSubstances();
    } else if (button.dataset.saveScan) {
      await api(`/scans/${button.dataset.saveScan}/medication`, { method: "POST", body: JSON.stringify({}) });
      setStatus("Scan saved as medication");
      await Promise.all([refreshScans(), refreshMedications()]);
    } else if (form?.dataset.medUploadForm) {
      await handleMedicationUpload(form);
    } else if (form?.dataset.medCameraForm) {
      await handleMedicationCamera(form);
    } else if (form?.dataset.uploadForm) {
      await handleUpload(form);
    } else if (form?.dataset.cameraForm) {
      await handleCamera(form);
    } else if (form?.dataset.endpoint) {
      await handleForm(form);
    }
  } catch (error) {
    if (error.message === "Please login first.") {
      requireLogin();
    } else {
      setStatus(error.message, true);
    }
  } finally {
    setButtonLoading(button, false);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const registeredEmail = new URLSearchParams(window.location.search).get("registered");
  if (registeredEmail) {
    const emailInput = document.querySelector('form[data-endpoint="POST /auth/login"] input[name="email"]');
    if (emailInput) emailInput.value = registeredEmail;
    setStatus("Registration complete. Please login with your password.");
  }
  showCurrentUser().catch(() => {});
  renderDashboardSummary().catch(() => {});
  renderRiskSummary().catch(() => {});
  renderTimeline().catch(() => {});
  renderAdherence().catch(() => {});
  refreshMedications().catch(() => {});
  refreshScans().catch(() => {});
  refreshSubstances().catch(() => {});
  refreshSideEffects().catch(() => {});
  renderSideEffectSummary().catch(() => {});
  renderAssistantStatus().catch(() => {});
  document.querySelectorAll('[data-endpoint="GET /interactions/history"] tbody').forEach((table) => {
    renderInteractionHistory(table).catch(() => {});
  });
});
