import React from "react";

function Login() {
  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Welcome Back</h1>
        <p className="page-subtitle">Sign in to access your schedule and tasks.</p>
      </div>

      <div className="card" style={{ maxWidth: 420 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.82rem",
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                marginBottom: "var(--space-xs)",
              }}
            >
              Email
            </label>
            <input
              type="email"
              placeholder="student@ufl.edu"
              disabled
              style={{
                width: "100%",
                padding: "0.6rem 0.8rem",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.9rem",
                fontFamily: "var(--font-sans)",
                background: "var(--color-bg)",
                color: "var(--color-text-muted)",
              }}
            />
          </div>
          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.82rem",
                fontWeight: 600,
                color: "var(--color-text-secondary)",
                marginBottom: "var(--space-xs)",
              }}
            >
              Password
            </label>
            <input
              type="password"
              placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"
              disabled
              style={{
                width: "100%",
                padding: "0.6rem 0.8rem",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.9rem",
                fontFamily: "var(--font-sans)",
                background: "var(--color-bg)",
                color: "var(--color-text-muted)",
              }}
            />
          </div>
          <button
            disabled
            className="quick-action-btn primary"
            style={{
              justifyContent: "center",
              padding: "0.7rem",
              marginTop: "var(--space-sm)",
              opacity: 0.6,
            }}
          >
            Sign In (Coming Soon)
          </button>
          <p
            style={{
              fontSize: "0.78rem",
              color: "var(--color-text-muted)",
              textAlign: "center",
            }}
          >
            Authentication will be implemented in a future sprint.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
