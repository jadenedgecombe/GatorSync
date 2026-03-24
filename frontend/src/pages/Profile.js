import React from "react";
import { useAuth } from "../context/AuthContext";

const ROLE_LABELS = { student: "Student", ta: "Teaching Assistant", admin: "Administrator" };
const ROLE_DESCRIPTIONS = {
  student: "You can view your dashboard, upload syllabi, manage your calendar, and join study groups.",
  ta: "You have student access plus the ability to view platform statistics in the Admin Panel.",
  admin: "You have full access to all features including user management and platform administration.",
};

function Profile() {
  const { user } = useAuth();

  if (!user) return null;

  const initials = user.display_name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <p className="page-subtitle">Your account details and access level.</p>
      </div>

      <div className="dashboard-grid">
        {/* Account Info */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-lg)", marginBottom: "var(--space-lg)" }}>
            <div className="profile-avatar-lg">{initials}</div>
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 2 }}>{user.display_name}</h2>
              <p style={{ color: "var(--color-text-secondary)", fontSize: "0.9rem" }}>{user.email}</p>
            </div>
          </div>

          <div className="profile-details">
            <div className="profile-row">
              <span className="profile-label">Display Name</span>
              <span className="profile-value">{user.display_name}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">Email</span>
              <span className="profile-value">{user.email}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">User ID</span>
              <span className="profile-value" style={{ fontFamily: "monospace", fontSize: "0.78rem" }}>{user.id}</span>
            </div>
          </div>
        </div>

        {/* Role & Access */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Role & Access</h3>
          </div>

          <div className="role-display">
            <div className={`role-badge-lg ${user.role}`}>
              {user.role === "admin" ? "\uD83D\uDD11" : user.role === "ta" ? "\uD83C\uDF93" : "\uD83D\uDCDA"}
              <span>{ROLE_LABELS[user.role] || user.role}</span>
            </div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "0.88rem", marginTop: "var(--space-md)", lineHeight: 1.6 }}>
              {ROLE_DESCRIPTIONS[user.role] || "Standard access."}
            </p>
          </div>

          <div style={{ marginTop: "var(--space-lg)" }}>
            <h4 style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "var(--space-sm)" }}>
              Your Permissions
            </h4>
            <div className="permissions-list">
              <div className="permission-item granted">Dashboard</div>
              <div className="permission-item granted">Syllabus Upload</div>
              <div className="permission-item granted">Calendar</div>
              <div className="permission-item granted">Study Groups</div>
              <div className={`permission-item ${user.role === "ta" || user.role === "admin" ? "granted" : "denied"}`}>
                Admin Panel — Stats
              </div>
              <div className={`permission-item ${user.role === "admin" ? "granted" : "denied"}`}>
                Admin Panel — User Management
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
