import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function AdminPanel() {
  const { token, user } = useAuth();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    // Fetch users (admin only)
    if (user?.role === "admin") {
      fetch(`${API}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => {
          if (res.status === 403) throw new Error("You don't have permission to view this");
          if (!res.ok) throw new Error("Failed to load users");
          return res.json();
        })
        .then(setUsers)
        .catch((err) => setError(err.message));
    }

    // Fetch stats (ta or admin)
    fetch(`${API}/admin/dashboard-stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.status === 403) return null;
        if (!res.ok) throw new Error("Failed to load stats");
        return res.json();
      })
      .then((data) => { if (data) setStats(data); })
      .catch(() => {});
  }, [token, user]);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Admin Panel</h1>
        <p className="page-subtitle">
          Manage users and view platform statistics.
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "0.6rem 0.8rem",
            background: "var(--color-danger-light)",
            color: "var(--color-danger)",
            borderRadius: "var(--radius-sm)",
            fontSize: "0.85rem",
            fontWeight: 500,
            marginBottom: "var(--space-lg)",
          }}
        >
          {error}
        </div>
      )}

      {/* Stats (visible to ta + admin) */}
      {stats && (
        <div className="stats-grid" style={{ marginBottom: "var(--space-xl)" }}>
          <div className="stat-card">
            <div className="stat-icon blue">{"\uD83D\uDC65"}</div>
            <div className="stat-value">{stats.total_users}</div>
            <div className="stat-label">Total Users</div>
          </div>
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <div className="stat-card" key={role}>
              <div className={`stat-icon ${role === "admin" ? "red" : role === "ta" ? "orange" : "green"}`}>
                {role === "admin" ? "\uD83D\uDD11" : role === "ta" ? "\uD83C\uDF93" : "\uD83D\uDCDA"}
              </div>
              <div className="stat-value">{count}</div>
              <div className="stat-label" style={{ textTransform: "capitalize" }}>{role}s</div>
            </div>
          ))}
        </div>
      )}

      {/* User table (admin only) */}
      {user?.role === "admin" && users.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">All Users</h3>
            <span className="card-badge">{users.length} users</span>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--color-border)" }}>
                <th style={{ textAlign: "left", padding: "0.6rem 0", color: "var(--color-text-secondary)", fontWeight: 600 }}>Name</th>
                <th style={{ textAlign: "left", padding: "0.6rem 0", color: "var(--color-text-secondary)", fontWeight: 600 }}>Email</th>
                <th style={{ textAlign: "left", padding: "0.6rem 0", color: "var(--color-text-secondary)", fontWeight: 600 }}>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "0.6rem 0" }}>{u.display_name}</td>
                  <td style={{ padding: "0.6rem 0", color: "var(--color-text-secondary)" }}>{u.email}</td>
                  <td style={{ padding: "0.6rem 0" }}>
                    <span className={`task-tag ${u.role === "admin" ? "urgent" : u.role === "ta" ? "soon" : "normal"}`}>
                      {u.role}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;
