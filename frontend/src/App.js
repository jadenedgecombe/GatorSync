import React, { useState } from "react";
import { Routes, Route, NavLink, Link, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import ErrorBoundary from "./components/ErrorBoundary";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import SyllabusUpload from "./pages/SyllabusUpload";
import Calendar from "./pages/Calendar";
import Templates from "./pages/Templates";
import AdminPanel from "./pages/AdminPanel";
import Profile from "./pages/Profile";
import Forbidden from "./pages/Forbidden";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, loading, logout } = useAuth();

  const closeSidebar = () => setSidebarOpen(false);

  const isAuthPage = location.pathname === "/login" || location.pathname === "/signup";

  if (loading && !isAuthPage) {
    return null;
  }

  if (isAuthPage) {
    return (
      <div className="auth-layout">
        <div className="auth-layout-brand">
          <Link to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div className="sidebar-logo">G</div>
            <span className="sidebar-brand-text">GatorSync</span>
          </Link>
        </div>
        <main className="auth-layout-content">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Routes>
        </main>
      </div>
    );
  }

  const isStaff = user && (user.role === "admin" || user.role === "ta");

  return (
    <div className="app-layout">
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? "✕" : "☰"}
      </button>

      <div
        className={`sidebar-overlay ${sidebarOpen ? "open" : ""}`}
        onClick={closeSidebar}
      />

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <Link to="/" className="sidebar-brand" onClick={closeSidebar}>
          <div className="sidebar-logo">G</div>
          <span className="sidebar-brand-text">GatorSync</span>
        </Link>

        <nav className="sidebar-nav">
          <span className="sidebar-section-label">Menu</span>

          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `sidebar-link ${isActive || location.pathname === "/" ? "active" : ""}`
            }
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"📊"}</span>
            Dashboard
          </NavLink>

          <NavLink
            to="/upload"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"📄"}</span>
            Syllabus Upload
          </NavLink>

          <NavLink
            to="/calendar"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"📅"}</span>
            Calendar
          </NavLink>

          <NavLink
            to="/templates"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"📚"}</span>
            Templates
          </NavLink>

          {isStaff && (
            <>
              <span className="sidebar-section-label">Staff</span>
              <NavLink
                to="/admin"
                className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
                onClick={closeSidebar}
              >
                <span className="sidebar-link-icon">{"⚙️"}</span>
                Admin Panel
              </NavLink>
            </>
          )}

          <span className="sidebar-section-label">Account</span>

          <NavLink
            to="/profile"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"👤"}</span>
            My Profile
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          {user ? (
            <div className="sidebar-user">
              <div className="sidebar-avatar">
                {user.display_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)}
              </div>
              <div className="sidebar-user-info">
                <span className="sidebar-user-name">{user.display_name}</span>
                <span className="sidebar-user-email">{user.email}</span>
              </div>
              <button
                onClick={logout}
                className="sidebar-logout-btn"
                title="Log out"
              >
                {"→"}
              </button>
            </div>
          ) : (
            <Link to="/login" className="quick-action-btn primary" style={{ width: "100%", justifyContent: "center" }}>
              Sign In
            </Link>
          )}
        </div>
      </aside>

      <main className="main-content">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><SyllabusUpload /></ProtectedRoute>} />
            <Route path="/calendar" element={<ProtectedRoute><Calendar /></ProtectedRoute>} />
            <Route path="/templates" element={<ProtectedRoute><Templates /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/admin" element={
              <ProtectedRoute>
                {isStaff ? <AdminPanel /> : <Forbidden />}
              </ProtectedRoute>
            } />
            <Route path="/forbidden" element={<Forbidden />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}

export default App;
