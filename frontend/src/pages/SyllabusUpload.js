import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend, apiUpload } from "../api";

const ASSIGNMENT_TYPES = ["homework", "exam", "project", "reading", "quiz", "other"];

function SyllabusUpload() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [newCourseName, setNewCourseName] = useState("");
  const [newCourseCode, setNewCourseCode] = useState("");

  const [file, setFile] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [rows, setRows] = useState([]);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!token) return;
    apiGet("/courses", token)
      .then(setCourses)
      .catch((e) => setError(e.message));
  }, [token]);

  const onFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setRows([]);
    setError("");
    setSuccess("");
  };

  const onParse = async () => {
    if (!file) {
      setError("Choose a file first");
      return;
    }
    setParsing(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await apiUpload("/syllabus/parse", fd, token);
      if (!res.rows.length) {
        setError("Couldn't find any assignments in this syllabus — you can still add them manually.");
      }
      setRows(
        res.rows.map((r, i) => ({
          id: `parsed-${i}`,
          title: r.title,
          due_date: r.due_date || "",
          assignment_type: r.assignment_type,
          estimated_hours: r.estimated_hours,
          keep: true,
        }))
      );
    } catch (err) {
      setError(err.message || "Failed to parse syllabus");
    } finally {
      setParsing(false);
    }
  };

  const updateRow = (id, field, value) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, [field]: value } : r)));
  };

  const addEmptyRow = () => {
    setRows((prev) => [
      ...prev,
      {
        id: `new-${Date.now()}`,
        title: "",
        due_date: "",
        assignment_type: "homework",
        estimated_hours: 2,
        keep: true,
      },
    ]);
  };

  const createCourseIfNeeded = async () => {
    if (selectedCourseId) return selectedCourseId;
    if (!newCourseName.trim()) {
      throw new Error("Pick an existing course or enter a new course name");
    }
    const c = await apiSend(
      "/courses",
      "POST",
      { name: newCourseName.trim(), course_code: newCourseCode.trim() || null },
      token
    );
    return c.id;
  };

  const onImport = async () => {
    const keepRows = rows.filter((r) => r.keep && r.title.trim());
    if (keepRows.length === 0) {
      setError("Nothing to import — check at least one row and give it a title.");
      return;
    }
    setImporting(true);
    setError("");
    try {
      const courseId = await createCourseIfNeeded();
      const payload = {
        course_id: courseId,
        rows: keepRows.map((r) => ({
          title: r.title.trim(),
          due_date: r.due_date ? new Date(r.due_date + "T23:59:00Z").toISOString() : null,
          assignment_type: r.assignment_type,
          estimated_hours: Number(r.estimated_hours) || 2,
        })),
      };
      const res = await apiSend("/syllabus/import", "POST", payload, token);
      setSuccess(`Imported ${res.created_count} assignments. Redirecting to your calendar...`);
      setTimeout(() => navigate("/calendar"), 1200);
    } catch (err) {
      setError(err.message || "Import failed");
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Syllabus Upload</h1>
        <p className="page-subtitle">
          Upload a course syllabus and we'll extract deadlines, exams, and assignments — review before importing.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{success}</div>}

      <div className="card" style={{ marginBottom: "var(--space-lg)" }}>
        <div className="card-header">
          <h3 className="card-title">1. Choose destination course</h3>
        </div>
        <div style={{ display: "flex", gap: "var(--space-md)", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 220px" }}>
            <label className="form-label">Existing course</label>
            <select
              value={selectedCourseId}
              onChange={(e) => {
                setSelectedCourseId(e.target.value);
                if (e.target.value) {
                  setNewCourseName("");
                  setNewCourseCode("");
                }
              }}
              className="form-input"
            >
              <option value="">— Create new below —</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.course_code ? `${c.course_code} — ` : ""}{c.name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ flex: "2 1 260px", display: "flex", gap: "var(--space-sm)" }}>
            <div style={{ flex: 2 }}>
              <label className="form-label">Or new course name</label>
              <input
                value={newCourseName}
                onChange={(e) => {
                  setNewCourseName(e.target.value);
                  if (e.target.value) setSelectedCourseId("");
                }}
                placeholder="e.g. Software Engineering"
                className="form-input"
              />
            </div>
            <div style={{ flex: 1 }}>
              <label className="form-label">Code</label>
              <input
                value={newCourseCode}
                onChange={(e) => setNewCourseCode(e.target.value)}
                placeholder="CEN 3031"
                className="form-input"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "var(--space-lg)" }}>
        <div className="card-header">
          <h3 className="card-title">2. Upload {user?.display_name?.split(" ")[0]}'s syllabus</h3>
        </div>

        <div
          className="upload-zone"
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={onFileChange}
            style={{ display: "none" }}
          />
          <div className="upload-icon">{"📁"}</div>
          <div className="upload-text">
            {file ? file.name : "Click to choose a PDF, DOCX, or TXT file"}
          </div>
          <div className="upload-hint">Supports PDF, DOCX, and TXT — up to 10 MB</div>
        </div>

        <div style={{ display: "flex", gap: "var(--space-sm)", marginTop: "var(--space-md)" }}>
          <button
            className="quick-action-btn primary"
            onClick={onParse}
            disabled={!file || parsing}
          >
            {parsing ? "Parsing..." : "Parse Syllabus"}
          </button>
          <button className="quick-action-btn" onClick={addEmptyRow}>+ Add Row Manually</button>
        </div>
      </div>

      {rows.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">3. Review & import</h3>
            <span className="card-badge">{rows.filter((r) => r.keep).length} selected</span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="review-table">
              <thead>
                <tr>
                  <th>Keep</th>
                  <th>Title</th>
                  <th>Due date</th>
                  <th>Type</th>
                  <th>Est. hrs</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={r.keep}
                        onChange={(e) => updateRow(r.id, "keep", e.target.checked)}
                      />
                    </td>
                    <td>
                      <input
                        value={r.title}
                        onChange={(e) => updateRow(r.id, "title", e.target.value)}
                        className="form-input"
                      />
                    </td>
                    <td>
                      <input
                        type="date"
                        value={r.due_date || ""}
                        onChange={(e) => updateRow(r.id, "due_date", e.target.value)}
                        className="form-input"
                      />
                    </td>
                    <td>
                      <select
                        value={r.assignment_type}
                        onChange={(e) => updateRow(r.id, "assignment_type", e.target.value)}
                        className="form-input"
                      >
                        {ASSIGNMENT_TYPES.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        min="1"
                        max="40"
                        value={r.estimated_hours}
                        onChange={(e) => updateRow(r.id, "estimated_hours", e.target.value)}
                        className="form-input"
                        style={{ width: 70 }}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "var(--space-md)" }}>
            <button
              className="quick-action-btn primary"
              onClick={onImport}
              disabled={importing || !rows.some((r) => r.keep)}
            >
              {importing ? "Importing..." : `Import ${rows.filter((r) => r.keep).length} assignments`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SyllabusUpload;
