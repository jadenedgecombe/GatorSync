import React from "react";
import { Link } from "react-router-dom";

function Forbidden() {
  return (
    <div className="page">
      <div style={{ textAlign: "center", paddingTop: "var(--space-2xl)" }}>
        <div style={{ fontSize: "3rem", marginBottom: "var(--space-md)" }}>{"\uD83D\uDEAB"}</div>
        <h1 className="page-title" style={{ marginBottom: "var(--space-sm)" }}>Access Denied</h1>
        <p style={{ color: "var(--color-text-secondary)", fontSize: "0.95rem", maxWidth: 400, margin: "0 auto var(--space-xl)" }}>
          You don't have permission to view this page. If you think this is a mistake, contact your administrator.
        </p>
        <Link to="/dashboard" className="quick-action-btn primary">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}

export default Forbidden;
