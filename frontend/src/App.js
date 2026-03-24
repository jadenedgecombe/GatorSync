import React, { useState } from "react";
import { Routes, Route, NavLink, Link, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import SyllabusUpload from "./pages/SyllabusUpload";
import Calendar from "./pages/Calendar";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, loading, logout } = useAuth();

  const closeSidebar = () => setSidebarOpen(false);

  // Show minimal layout for login/signup (no sidebar)
  const isAuthPage = location.pathname === "/login" || location.pathname === "/signup";

  // While checking auth state, show nothing to prevent layout flicker
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

  return (
    <div className="app-layout">
      {/* Mobile menu button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? "\u2715" : "\u2630"}
      </button>

      {/* Overlay for mobile */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? "open" : ""}`}
        onClick={closeSidebar}
      />

      {/* Sidebar */}
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
            <span className="sidebar-link-icon">{"\uD83D\uDCCA"}</span>
            Dashboard
          </NavLink>

          <NavLink
            to="/upload"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"\uD83D\uDCC4"}</span>
            Syllabus Upload
          </NavLink>

          <NavLink
            to="/calendar"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"\uD83D\uDCC5"}</span>
            Calendar
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
                {"\u2192"}
              </button>
            </div>
          ) : (
            <Link to="/login" className="quick-action-btn primary" style={{ width: "100%", justifyContent: "center" }}>
              Sign In
            </Link>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><SyllabusUpload /></ProtectedRoute>} />
          <Route path="/calendar" element={<ProtectedRoute><Calendar /></ProtectedRoute>} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
