import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend } from "../api";

function formatRange(starts, ends) {
  const s = new Date(starts);
  const e = new Date(ends);
  const dateStr = s.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
  const startTime = s.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  const endTime = e.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  return `${dateStr} · ${startTime} – ${endTime}`;
}

function toLocalInputValue(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const EMPTY_FORM = { title: "", description: "", location: "", starts_at: "", ends_at: "" };

function StudySessions() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editId, setEditId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = () => {
    if (!token) return;
    setLoading(true);
    apiGet("/study-sessions", token)
      .then(setSessions)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [token]);

  const handleOpenNew = () => {
    setForm(EMPTY_FORM);
    setEditId(null);
    setError("");
    setShowForm(true);
  };

  const handleEdit = (s) => {
    setForm({
      title: s.title,
      description: s.description || "",
      location: s.location || "",
      starts_at: toLocalInputValue(s.starts_at),
      ends_at: toLocalInputValue(s.ends_at),
    });
    setEditId(s.id);
    setError("");
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this study session?")) return;
    try {
      await apiSend(`/study-sessions/${id}`, "DELETE", null, token);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch {
      alert("Failed to delete session.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = {
        title: form.title,
        description: form.description || null,
        location: form.location || null,
        starts_at: new Date(form.starts_at).toISOString(),
        ends_at: new Date(form.ends_at).toISOString(),
      };
      if (editId) {
        const updated = await apiSend(`/study-sessions/${editId}`, "PATCH", payload, token);
        setSessions((prev) => prev.map((s) => (s.id === editId ? updated : s)));
      } else {
        const created = await apiSend("/study-sessions", "POST", payload, token);
        setSessions((prev) => [...prev, created].sort((a, b) => new Date(a.starts_at) - new Date(b.starts_at)));
      }
      setShowForm(false);
      setForm(EMPTY_FORM);
      setEditId(null);
    } catch (err) {
      setError(err.message || "Failed to save session.");
    } finally {
      setSaving(false);
    }
  };

  const upcoming = sessions.filter((s) => new Date(s.ends_at) >= new Date());
  const past = sessions.filter((s) => new Date(s.ends_at) < new Date());

  return (
    <div className="page">
      <div className="page-header" style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <h1 className="page-title">Study Sessions</h1>
          <p className="page-subtitle">Schedule and track your personal study blocks.</p>
        </div>
        <button
          className="btn-primary"
          onClick={handleOpenNew}
          aria-label="Create new study session"
        >
          + New Session
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Study session form">
          <div className="modal-card">
            <div className="modal-header">
              <h2 className="card-title">{editId ? "Edit Session" : "New Study Session"}</h2>
              <button
                className="modal-close"
                onClick={() => setShowForm(false)}
                aria-label="Close form"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="session-title">Title *</label>
                <input
                  id="session-title"
                  className="form-input"
                  value={form.title}
                  onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                  placeholder="e.g. COP 3530 — Midterm Review"
                  required
                  aria-required="true"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="session-location">Location</label>
                <input
                  id="session-location"
                  className="form-input"
                  value={form.location}
                  onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
                  placeholder="e.g. Library Room 204"
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-md)" }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="session-start">Start *</label>
                  <input
                    id="session-start"
                    type="datetime-local"
                    className="form-input"
                    value={form.starts_at}
                    onChange={(e) => setForm((f) => ({ ...f, starts_at: e.target.value }))}
                    required
                    aria-required="true"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="session-end">End *</label>
                  <input
                    id="session-end"
                    type="datetime-local"
                    className="form-input"
                    value={form.ends_at}
                    onChange={(e) => setForm((f) => ({ ...f, ends_at: e.target.value }))}
                    required
                    aria-required="true"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="session-desc">Description</label>
                <textarea
                  id="session-desc"
                  className="form-input"
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  placeholder="Topics to cover, goals for the session…"
                  style={{ resize: "vertical" }}
                />
              </div>

              {error && (
                <div className="form-error" role="alert">{error}</div>
              )}

              <div style={{ display: "flex", gap: "var(--space-sm)", justifyContent: "flex-end", marginTop: "var(--space-lg)" }}>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={saving} aria-busy={saving}>
                  {saving ? "Saving…" : editId ? "Update Session" : "Create Session"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty-state"><p className="empty-state-text">Loading sessions…</p></div>
      ) : sessions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📖</div>
          <p className="empty-state-text">No study sessions yet. Create one to get started!</p>
        </div>
      ) : (
        <>
          {upcoming.length > 0 && (
            <section aria-label="Upcoming sessions">
              <h2 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "var(--space-md)" }}>
                Upcoming ({upcoming.length})
              </h2>
              <div className="sessions-grid">
                {upcoming.map((s) => (
                  <SessionCard key={s.id} session={s} onEdit={handleEdit} onDelete={handleDelete} />
                ))}
              </div>
            </section>
          )}

          {past.length > 0 && (
            <section aria-label="Past sessions" style={{ marginTop: "var(--space-xl)" }}>
              <h2 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "var(--space-md)" }}>
                Past ({past.length})
              </h2>
              <div className="sessions-grid" style={{ opacity: 0.7 }}>
                {past.map((s) => (
                  <SessionCard key={s.id} session={s} onEdit={handleEdit} onDelete={handleDelete} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

function SessionCard({ session: s, onEdit, onDelete }) {
  const durationMs = new Date(s.ends_at) - new Date(s.starts_at);
  const durationMin = Math.round(durationMs / 60000);
  const hrs = Math.floor(durationMin / 60);
  const mins = durationMin % 60;
  const durationLabel = hrs > 0
    ? `${hrs}h${mins > 0 ? ` ${mins}m` : ""}`
    : `${mins}m`;

  return (
    <article className="card session-card" aria-label={`Study session: ${s.title}`}>
      <div className="session-card-header">
        <span className="session-icon" aria-hidden="true">📖</span>
        <div style={{ flex: 1 }}>
          <div className="session-title">{s.title}</div>
          <div className="session-time">{formatRange(s.starts_at, s.ends_at)}</div>
        </div>
        <span className="session-duration">{durationLabel}</span>
      </div>

      {(s.location || s.description) && (
        <div className="session-body">
          {s.location && (
            <div className="session-location">
              <span aria-hidden="true">📍</span> {s.location}
            </div>
          )}
          {s.description && (
            <div className="session-desc">{s.description}</div>
          )}
        </div>
      )}

      <div className="session-actions">
        <button
          className="btn-ghost"
          onClick={() => onEdit(s)}
          aria-label={`Edit ${s.title}`}
        >
          Edit
        </button>
        <button
          className="btn-danger-ghost"
          onClick={() => onDelete(s.id)}
          aria-label={`Delete ${s.title}`}
        >
          Delete
        </button>
      </div>
    </article>
  );
}

export default StudySessions;
