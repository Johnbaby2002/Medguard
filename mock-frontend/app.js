const state = {
  token: localStorage.getItem("medguard_token") || "",
  lastMedicationId: localStorage.getItem("medguard_medication_id") || "",
  lastReminderId: localStorage.getItem("medguard_reminder_id") || "",
};

const el = (id) => document.getElementById(id);

function apiBase() {
  return el("apiBase").value.replace(/\/$/, "");
}

function authHeaders() {
  return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

function show(value) {
  el("output").textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function setToken(token) {
  state.token = token;
  localStorage.setItem("medguard_token", token);
  el("authState").textContent = token ? "Token saved for requests" : "No token yet";
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(JSON.stringify(data, null, 2));
  }
  show(data || `${response.status} ${response.statusText}`);
  return data;
}

function renderCards(data) {
  el("dashboardCards").innerHTML = [
    ["Active meds", data.active_medications],
    ["Reminders", data.active_reminders],
    ["Taken doses", data.taken_doses],
    ["Missed doses", data.missed_doses],
  ]
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`)
    .join("");
}

function renderList(targetId, items, formatter) {
  el(targetId).innerHTML = items.length
    ? items.map(formatter).join("")
    : '<div class="item">No records yet.</div>';
}

function medicationPayload() {
  return {
    name: el("medName").value,
    active_ingredient: el("medIngredients").value,
    dosage: el("medStrength").value,
    form: el("medForm").value,
    frequency: el("medFrequency").value,
    medication_category: el("medIngredients").value.toLowerCase().includes("warfarin") ? "blood thinner" : "",
    is_prescription: true,
    notes: el("medInstructions").value,
  };
}

async function guard(fn) {
  try {
    await fn();
  } catch (error) {
    show(error.message);
  }
}

el("registerBtn").addEventListener("click", () =>
  guard(async () => {
    const data = await request("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: el("email").value,
        password: el("password").value,
        full_name: el("fullName").value,
        role: el("role").value,
      }),
    });
    setToken(data.access_token);
  })
);

el("loginBtn").addEventListener("click", () =>
  guard(async () => {
    const data = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: el("email").value, password: el("password").value }),
    });
    setToken(data.access_token);
  })
);

el("meBtn").addEventListener("click", () => guard(() => request("/auth/me")));

el("dashboardBtn").addEventListener("click", () =>
  guard(async () => {
    const data = await request("/dashboard");
    renderCards(data);
  })
);

el("addMedBtn").addEventListener("click", () =>
  guard(async () => {
    const med = await request("/medications", { method: "POST", body: JSON.stringify(medicationPayload()) });
    state.lastMedicationId = med.id;
    localStorage.setItem("medguard_medication_id", med.id);
    el("selectedMedicationId").value = med.id;
  })
);

el("listMedsBtn").addEventListener("click", () =>
  guard(async () => {
    const meds = await request("/medications");
    if (meds[0]) {
      state.lastMedicationId = meds[0].id;
      localStorage.setItem("medguard_medication_id", meds[0].id);
      el("selectedMedicationId").value = meds[0].id;
    }
    renderList(
      "medList",
      meds,
      (med) => `<div class="item"><strong>${med.name} ${med.dosage || ""}</strong><code>${med.id}</code></div>`
    );
  })
);

el("addReminderBtn").addEventListener("click", () =>
  guard(async () => {
    const medicationId = el("selectedMedicationId").value || state.lastMedicationId;
    const reminder = await request("/reminders", {
      method: "POST",
      body: JSON.stringify({
        medication_id: medicationId,
        time: el("reminderTime").value,
        repeat_pattern: "daily",
        timezone: "Europe/Berlin",
      }),
    });
    state.lastReminderId = reminder.id;
    localStorage.setItem("medguard_reminder_id", reminder.id);
  })
);

el("listRemindersBtn").addEventListener("click", () =>
  guard(async () => {
    const reminders = await request("/reminders/today");
    if (reminders[0]) {
      state.lastReminderId = reminders[0].id;
      localStorage.setItem("medguard_reminder_id", reminders[0].id);
    }
    renderList(
      "reminderList",
      reminders,
      (reminder) => `<div class="item"><strong>${reminder.medication_name || "Medication"} at ${reminder.time}</strong><code>${reminder.id}</code></div>`
    );
  })
);

el("logDoseBtn").addEventListener("click", () =>
  guard(async () => {
    const reminderId = state.lastReminderId;
    const status = el("doseStatus").value === "missed" ? "missed" : "taken";
    await request(`/reminders/${reminderId}/${status}`, { method: "POST", body: JSON.stringify({}) });
  })
);

el("listDosesBtn").addEventListener("click", () =>
  guard(async () => {
    const logs = await request("/reminders/today");
    renderList(
      "doseList",
      logs,
      (reminder) => `<div class="item"><strong>${reminder.medication_name}</strong><code>taken=${reminder.taken_status} missed=${reminder.missed_status}</code></div>`
    );
  })
);

el("createSafetyBtn").addEventListener("click", () =>
  guard(async () => {
    await request("/safety-check", {
      method: "POST",
      body: JSON.stringify({}),
    });
  })
);

el("listSafetyBtn").addEventListener("click", () =>
  guard(async () => {
    const checks = await request("/interactions/history");
    renderList(
      "safetyList",
      checks,
      (check) =>
        `<div class="item"><strong>${check.highest_severity || "none"}</strong><code>${check.id}</code><pre>${JSON.stringify(check.interactions, null, 2)}</pre></div>`
    );
  })
);

el("createReportBtn").addEventListener("click", () =>
  guard(() => request("/reports/medication-summary"))
);

el("listReportsBtn").addEventListener("click", () =>
  guard(async () => {
    const reports = [await request("/reports/medication-summary")];
    renderList(
      "reportList",
      reports,
      (report) => `<div class="item"><strong>Medication Summary</strong><code>risks=${report.detected_risks.interactions.length}</code></div>`
    );
  })
);

el("shareBtn").addEventListener("click", () =>
  guard(() =>
    request("/caregiver/invite", {
      method: "POST",
      body: JSON.stringify({
        caregiver_email: el("caregiverEmail").value,
        relationship: "family caregiver",
        can_manage: false,
        missed_dose_alerts: true,
      }),
    })
  )
);

el("listCaregiversBtn").addEventListener("click", () =>
  guard(async () => {
    const caregivers = await request("/caregiver/patients");
    renderList(
      "caregiverList",
      caregivers,
      (patient) => `<div class="item"><strong>${patient.full_name}</strong><code>${patient.email}</code></div>`
    );
  })
);

setToken(state.token);
el("selectedMedicationId").value = state.lastMedicationId;
