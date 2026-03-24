import React, { useState } from "react";
import { Routes, Route, NavLink, Link, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import SyllabusUpload from "./pages/SyllabusUpload";
import Calendar from "./pages/Calendar";
import "./App.css";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const closeSidebar = () => setSidebarOpen(false);

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

          <span className="sidebar-section-label">Account</span>

          <NavLink
            to="/login"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            onClick={closeSidebar}
          >
            <span className="sidebar-link-icon">{"\uD83D\uDD11"}</span>
            Login
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">GS</div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">Gator Student</span>
              <span className="sidebar-user-email">student@ufl.edu</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<SyllabusUpload />} />
          <Route path="/calendar" element={<Calendar />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
