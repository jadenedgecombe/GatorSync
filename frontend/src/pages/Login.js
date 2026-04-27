import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const inputStyle = {
  width: "100%",
  padding: "0.6rem 0.8rem",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--radius-sm)",
  fontSize: "0.9rem",
  fontFamily: "var(--font-sans)",
  background: "var(--color-surface)",
  color: "var(--color-text)",
};

const labelStyle = {
  display: "block",
  fontSize: "0.82rem",
  fontWeight: 600,
  color: "var(--color-text-secondary)",
  marginBottom: "var(--space-xs)",
};

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Welcome Back</h1>
        <p className="page-subtitle">Sign in to access your schedule and tasks.</p>
      </div>

      <div className="card" style={{ maxWidth: 420 }}>
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)" }}
        >
          {error && (
            <div
              style={{
                padding: "0.6rem 0.8rem",
                background: "var(--color-danger-light)",
                color: "var(--color-danger)",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.85rem",
                fontWeight: 500,
              }}
            >
              {error}
            </div>
          )}

          <div>
            <label htmlFor="login-email" style={labelStyle}>Email</label>
            <input
              id="login-email"
              type="email"
              placeholder="student@ufl.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
              autoComplete="email"
              style={inputStyle}
            />
          </div>

          <div>
            <label htmlFor="login-password" style={labelStyle}>Password</label>
            <input
              id="login-password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              aria-required="true"
              autoComplete="current-password"
              style={inputStyle}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="quick-action-btn primary"
            style={{
              justifyContent: "center",
              padding: "0.7rem",
              marginTop: "var(--space-sm)",
              opacity: submitting ? 0.6 : 1,
            }}
          >
            {submitting ? "Signing in..." : "Sign In"}
          </button>

          <p
            style={{
              fontSize: "0.82rem",
              color: "var(--color-text-muted)",
              textAlign: "center",
            }}
          >
            Don't have an account?{" "}
            <Link to="/signup" style={{ color: "var(--color-primary)", fontWeight: 600 }}>
              Sign up
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;
