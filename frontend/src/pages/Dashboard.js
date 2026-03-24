import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/* ---- Mock data ---- */
const stats = [
  { icon: "\uD83D\uDCDA", label: "Active Courses", value: "5", color: "blue" },
  { icon: "\u2705", label: "Tasks Done", value: "23", color: "green" },
  { icon: "\u23F3", label: "Upcoming Due", value: "8", color: "orange" },
  { icon: "\uD83D\uDD14", label: "Reminders Today", value: "3", color: "red" },
];

const tasks = [
  { name: "CDA 3101 — Homework 5", meta: "Due Tomorrow, 11:59 PM", tag: "urgent" },
  { name: "COP 3530 — Project 2 Report", meta: "Due Mar 28", tag: "soon" },
  { name: "ENC 3246 — Peer Review Draft", meta: "Due Mar 30", tag: "normal" },
  { name: "CEN 3031 — Sprint 1 Deliverable", meta: "Due Apr 1", tag: "normal" },
  { name: "STA 3032 — Practice Exam", meta: "Due Apr 3", tag: "normal" },
];

const reminders = [
  { text: "Office hours with Prof. Davis", time: "Today, 2:00 PM", dot: "blue" },
  { text: "Study group — Data Structures", time: "Today, 5:30 PM", dot: "green" },
  { text: "Register for Fall courses", time: "Tomorrow, 9:00 AM", dot: "orange" },
  { text: "CDA 3101 exam review session", time: "Wed, 3:00 PM", dot: "red" },
];

const schedule = [
  { time: "9:00", name: "COP 3530 — Data Structures", location: "CSE E121", color: "blue" },
  { time: "11:00", name: "CDA 3101 — Computer Organization", location: "NEB 202", color: "green" },
  { time: "1:00", name: "ENC 3246 — Professional Writing", location: "TUR 2322", color: "orange" },
  { time: "3:30", name: "CEN 3031 — Software Engineering", location: "CSE E116", color: "blue" },
];

/* ---- Mini calendar helper ---- */
function MiniCalendar() {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const eventDays = [5, 12, 15, 19, 22, 28];

  const cells = [];
  for (let i = 0; i < firstDay; i++) {
    cells.push(<div key={`e${i}`} className="calendar-day empty" />);
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate();
    const hasEvent = eventDays.includes(d);
    cells.push(
      <div
        key={d}
        className={`calendar-day${isToday ? " today" : ""}${hasEvent ? " has-event" : ""}`}
      >
        {d}
      </div>
    );
  }

  const monthName = today.toLocaleString("default", { month: "long", year: "numeric" });

  return (
    <>
      <div className="card-header">
        <h3 className="card-title">{monthName}</h3>
      </div>
      <div className="calendar-mini">
        {days.map((d) => (
          <div key={d} className="calendar-day-header">{d}</div>
        ))}
        {cells}
      </div>
    </>
  );
}

/* ---- Dashboard ---- */
function Dashboard() {
  const { user } = useAuth();
  const firstName = user?.display_name?.split(" ")[0] || "Gator";

  return (
    <div className="page">
      {/* Hero */}
      <div className="hero-banner">
        <h1 className="hero-greeting">Good morning, {firstName}!</h1>
        <p className="hero-message">
          You have 8 upcoming tasks and 3 reminders today. Stay on track — you're doing great.
        </p>
        <div className="hero-actions">
          <Link to="/upload" className="hero-btn white">
            {"\uD83D\uDCC4"} Upload Syllabus
          </Link>
          <Link to="/calendar" className="hero-btn ghost">
            {"\uD83D\uDCC5"} View Calendar
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map((s, i) => (
          <div className="stat-card" key={i}>
            <div className={`stat-icon ${s.color}`}>{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div style={{ marginBottom: "var(--space-xl)" }}>
        <div className="quick-actions">
          <Link to="/upload" className="quick-action-btn primary">
            + Upload Syllabus
          </Link>
          <button className="quick-action-btn">{"\uD83D\uDCE4"} Export Schedule</button>
          <button className="quick-action-btn">{"\uD83D\uDC65"} Find Study Group</button>
          <button className="quick-action-btn">{"\u2699\uFE0F"} Preferences</button>
        </div>
      </div>

      {/* Two-column grid */}
      <div className="dashboard-grid">
        {/* Upcoming Tasks */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Upcoming Tasks</h3>
            <span className="card-badge">{tasks.length} pending</span>
          </div>
          <ul className="task-list">
            {tasks.map((t, i) => (
              <li className="task-item" key={i}>
                <div className="task-checkbox" />
                <div className="task-info">
                  <div className="task-name">{t.name}</div>
                  <div className="task-meta">{t.meta}</div>
                </div>
                <span className={`task-tag ${t.tag}`}>
                  {t.tag === "urgent" ? "Urgent" : t.tag === "soon" ? "Soon" : "Upcoming"}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Reminders */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Reminders</h3>
            <span className="card-badge">{reminders.length} today</span>
          </div>
          <div className="reminder-list">
            {reminders.map((r, i) => (
              <div className="reminder-item" key={i}>
                <div className={`reminder-dot ${r.dot}`} />
                <div>
                  <div className="reminder-text">{r.text}</div>
                  <div className="reminder-time">{r.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Today's Schedule */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Today's Schedule</h3>
            <span className="card-badge">
              {schedule.length} classes
            </span>
          </div>
          {schedule.map((s, i) => (
            <div className="schedule-item" key={i}>
              <span className="schedule-time">{s.time}</span>
              <div className={`schedule-bar ${s.color}`} />
              <div className="schedule-details">
                <div className="schedule-name">{s.name}</div>
                <div className="schedule-location">{s.location}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Mini Calendar */}
        <div className="card">
          <MiniCalendar />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
