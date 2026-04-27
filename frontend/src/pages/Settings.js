import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend } from "../api";

const TIMEZONES = [
  { value: "America/New_York", label: "Eastern (ET)" },
  { value: "America/Chicago", label: "Central (CT)" },
  { value: "America/Denver", label: "Mountain (MT)" },
  { value: "America/Los_Angeles", label: "Pacific (PT)" },
  { value: "America/Phoenix", label: "Arizona (no DST)" },
  { value: "America/Anchorage", label: "Alaska (AKT)" },
  { value: "Pacific/Honolulu", label: "Hawaii (HST)" },
  { value: "UTC", label: "UTC" },
];

function Settings() {
  const { token } = useAuth();
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    apiGet("/preferences", token)
      .then(setPrefs)
      .catch(() => setError("Failed to load preferences."));
  }, [token]);

  const handleChange = (field, value) => {
    setPrefs((p) => ({ ...p, [field]: value }));
    setSaved(false);

    if (field === "dark_mode") {
      document.documentElement.setAttribute("data-theme", value ? "dark" : "light");
      localStorage.setItem("dark_mode", value ? "1" : "0");
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const updated = await apiSend("/preferences", "PATCH", prefs, token);
      setPrefs(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setError(err.message || "Failed to save preferences.");
    } finally {
      setSaving(false);
    }
  };

  if (!prefs) {
    return (
      <div className="page">
        <div className="empty-state">
          <p className="empty-state-text">{error || "Loading settings..."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your display and notification preferences.</p>
      </div>

      <form onSubmit={handleSave} aria-label="User preferences form">
        <div className="dashboard-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
          {/* Appearance */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Appearance</h3>
            </div>

            <div className="settings-section">
              <label className="settings-row" htmlFor="dark-mode-toggle">
                <div>
                  <div className="settings-label">Dark Mode</div>
                  <div className="settings-desc">Switch the interface to a dark colour scheme.</div>
                </div>
                <button
                  id="dark-mode-toggle"
                  type="button"
                  role="switch"
                  aria-checked={prefs.dark_mode}
                  className={`toggle-switch ${prefs.dark_mode ? "on" : ""}`}
                  onClick={() => handleChange("dark_mode", !prefs.dark_mode)}
                  aria-label="Toggle dark mode"
                >
                  <span className="toggle-thumb" />
                </button>
              </label>

              <div className="settings-row">
                <div>
                  <div className="settings-label">Timezone</div>
                  <div className="settings-desc">Used for scheduling and calendar views.</div>
                </div>
                <select
                  value={prefs.timezone}
                  onChange={(e) => handleChange("timezone", e.target.value)}
                  className="settings-select"
                  aria-label="Select timezone"
                >
                  {TIMEZONES.map((tz) => (
                    <option key={tz.value} value={tz.value}>
                      {tz.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Notifications</h3>
            </div>

            <div className="settings-section">
              <label className="settings-row" htmlFor="email-notif-toggle">
                <div>
                  <div className="settings-label">Email Notifications</div>
                  <div className="settings-desc">Receive assignment reminders by email.</div>
                </div>
                <button
                  id="email-notif-toggle"
                  type="button"
                  role="switch"
                  aria-checked={prefs.notification_email}
                  className={`toggle-switch ${prefs.notification_email ? "on" : ""}`}
                  onClick={() => handleChange("notification_email", !prefs.notification_email)}
                  aria-label="Toggle email notifications"
                >
                  <span className="toggle-thumb" />
                </button>
              </label>

              <label className="settings-row" htmlFor="push-notif-toggle">
                <div>
                  <div className="settings-label">Push Notifications</div>
                  <div className="settings-desc">Receive in-app push reminders.</div>
                </div>
                <button
                  id="push-notif-toggle"
                  type="button"
                  role="switch"
                  aria-checked={prefs.notification_push}
                  className={`toggle-switch ${prefs.notification_push ? "on" : ""}`}
                  onClick={() => handleChange("notification_push", !prefs.notification_push)}
                  aria-label="Toggle push notifications"
                >
                  <span className="toggle-thumb" />
                </button>
              </label>
            </div>
          </div>
        </div>

        {error && (
          <div className="form-error" role="alert" style={{ marginTop: "var(--space-md)" }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: "var(--space-xl)", display: "flex", gap: "var(--space-md)", alignItems: "center" }}>
          <button
            type="submit"
            className="btn-primary"
            disabled={saving}
            aria-busy={saving}
          >
            {saving ? "Saving…" : "Save Settings"}
          </button>
          {saved && (
            <span style={{ color: "var(--color-success)", fontSize: "0.9rem", fontWeight: 600 }} role="status">
              ✓ Saved
            </span>
          )}
        </div>
      </form>
    </div>
  );
}

export default Settings;
