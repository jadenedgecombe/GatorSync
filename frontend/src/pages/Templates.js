import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend } from "../api";

function Templates() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [importingId, setImportingId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isStaff = user?.role === "admin" || user?.role === "ta";
  const [form, setForm] = useState({ name: "", course_code: "", semester: "", instructor: "" });
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!token) return;
    apiGet("/templates", token)
      .then(setTemplates)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  const onImport = async (templateId) => {
    setImportingId(templateId);
    setError("");
    try {
      const res = await apiSend(`/templates/${templateId}/import`, "POST", null, token);
      setSuccess(`Imported ${res.assignments_imported} assignments. Redirecting to your calendar...`);
      setTimeout(() => navigate("/calendar"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setImportingId(null);
    }
  };

  const onPublish = async (e) => {
    e.preventDefault();
    try {
      const t = await apiSend("/templates", "POST", form, token);
      setTemplates((prev) => [...prev, t]);
      setForm({ name: "", course_code: "", semester: "", instructor: "" });
      setSuccess("Template published.");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Course Templates</h1>
        <p className="page-subtitle">
          Import a ready-made course schedule into your workspace, or publish one for others.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{success}</div>}

      {isStaff && (
        <div className="card" style={{ marginBottom: "var(--space-lg)" }}>
          <div className="card-header">
            <h3 className="card-title">Publish a new template</h3>
          </div>
          <form onSubmit={onPublish} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "var(--space-md)" }}>
            <div>
              <label className="form-label">Course name</label>
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="form-input" />
            </div>
            <div>
              <label className="form-label">Code</label>
              <input value={form.course_code} onChange={(e) => setForm({ ...form, course_code: e.target.value })} className="form-input" />
            </div>
            <div>
              <label className="form-label">Semester</label>
              <input value={form.semester} onChange={(e) => setForm({ ...form, semester: e.target.value })} className="form-input" />
            </div>
            <div>
              <label className="form-label">Instructor</label>
              <input value={form.instructor} onChange={(e) => setForm({ ...form, instructor: e.target.value })} className="form-input" />
            </div>
            <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end" }}>
              <button className="quick-action-btn primary" type="submit">Publish Template</button>
            </div>
          </form>
          <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "var(--space-sm)" }}>
            After publishing, add assignments to the template through the Courses API or upload a syllabus targeting the template course.
          </p>
        </div>
      )}

      <div style={{ marginBottom: "var(--space-lg)" }}>
        <input
          className="form-input search-input"
          placeholder="Search templates by name, code, or semester…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search templates"
        />
      </div>

      {loading ? (
        <div className="empty-state"><p className="empty-state-text">Loading templates...</p></div>
      ) : templates.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">{"📚"}</div>
          <p className="empty-state-text">No templates published yet.</p>
        </div>
      ) : (
        <div className="template-grid">
          {templates.filter((t) => {
            if (!search) return true;
            const q = search.toLowerCase();
            return (
              t.name?.toLowerCase().includes(q) ||
              t.course_code?.toLowerCase().includes(q) ||
              t.semester?.toLowerCase().includes(q) ||
              t.instructor?.toLowerCase().includes(q)
            );
          }).map((t) => (
            <div className="card template-card" key={t.id}>
              <div className="template-code">{t.course_code || "—"}</div>
              <div className="template-name">{t.name}</div>
              <div className="template-meta">{t.semester} {t.instructor && `· ${t.instructor}`}</div>
              <div className="template-count">{t.assignment_count} assignments</div>
              <button
                className="quick-action-btn primary"
                onClick={() => onImport(t.id)}
                disabled={importingId === t.id}
              >
                {importingId === t.id ? "Importing..." : "Import into my workspace"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Templates;
