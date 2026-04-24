import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend } from "../api";

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

// Today in the user's local timezone, formatted as YYYY-MM-DD.
// Avoids the UTC-midnight off-by-one that shifts evening dates by a day.
function localTodayIso() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function taskTag(dueDate) {
  if (!dueDate) return { cls: "normal", label: "Upcoming" };
  const ms = new Date(dueDate).getTime() - Date.now();
  const days = ms / (1000 * 60 * 60 * 24);
  if (days <= 1) return { cls: "urgent", label: "Urgent" };
  if (days <= 3) return { cls: "soon", label: "Soon" };
  return { cls: "normal", label: "Upcoming" };
}

function formatDue(dueDate) {
  if (!dueDate) return "No due date";
  const d = new Date(dueDate);
  const now = new Date();
  const diffDays = Math.round((d - now) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return `Due Today, ${d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  if (diffDays === 1) return `Due Tomorrow, ${d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  return `Due ${d.toLocaleDateString([], { month: "short", day: "numeric" })}`;
}

function MiniCalendar({ eventDates }) {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const eventDayNumbers = new Set(
    eventDates
      .map((d) => new Date(d))
      .filter((d) => d.getFullYear() === year && d.getMonth() === month)
      .map((d) => d.getDate())
  );

  const cells = [];
  for (let i = 0; i < firstDay; i++) {
    cells.push(<div key={`e${i}`} className="calendar-day empty" />);
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate();
    const hasEvent = eventDayNumbers.has(d);
    cells.push(
      <div key={d} className={`calendar-day${isToday ? " today" : ""}${hasEvent ? " has-event" : ""}`}>
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

function Dashboard() {
  const { user, token } = useAuth();
  const [courses, setCourses] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [loading, setLoading] = useState(true);

  const firstName = user?.display_name?.split(" ")[0] || "Gator";
  const isStaff = user?.role === "admin" || user?.role === "ta";

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    const today = localTodayIso();
    Promise.all([
      apiGet("/courses", token),
      apiGet("/tasks", token),
      apiGet("/reminders", token),
      apiGet(`/schedule/day?date=${today}`, token),
    ])
      .then(([coursesRes, tasksRes, remindersRes, dayRes]) => {
        if (cancelled) return;
        setCourses(coursesRes);
        setTasks(tasksRes);
        setReminders(remindersRes);
        setTodaySchedule(dayRes.tasks || []);
      })
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [token]);

  const completedCount = useMemo(() => tasks.filter((t) => t.is_completed).length, [tasks]);
  const pendingTasks = useMemo(
    () =>
      tasks
        .filter((t) => !t.is_completed)
        .sort((a, b) => {
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date) - new Date(b.due_date);
        })
        .slice(0, 6),
    [tasks]
  );
  const upcomingCount = pendingTasks.length;
  const remindersTodayCount = useMemo(() => {
    const today = new Date().toDateString();
    return reminders.filter((r) => new Date(r.remind_at).toDateString() === today).length;
  }, [reminders]);

  const stats = [
    { icon: "📚", label: "Active Courses", value: String(courses.length), color: "blue" },
    { icon: "✅", label: "Tasks Done", value: String(completedCount), color: "green" },
    { icon: "⏳", label: "Upcoming Due", value: String(upcomingCount), color: "orange" },
    { icon: "🔔", label: "Reminders Today", value: String(remindersTodayCount), color: "red" },
  ];

  const heroMessage = isStaff
    ? `You're signed in as ${user.role === "admin" ? "an administrator" : "a teaching assistant"}. ${upcomingCount} upcoming tasks and ${remindersTodayCount} reminders today.`
    : `You have ${upcomingCount} upcoming task${upcomingCount === 1 ? "" : "s"} and ${remindersTodayCount} reminder${remindersTodayCount === 1 ? "" : "s"} today. Stay on track.`;

  const dismissReminder = (id) => {
    apiSend(`/reminders/${id}/dismiss`, "POST", null, token)
      .then(() => setReminders((prev) => prev.filter((r) => r.id !== id)))
      .catch(() => {});
  };

  return (
    <div className="page">
      <div className="hero-banner">
        <h1 className="hero-greeting">{getGreeting()}, {firstName}!</h1>
        <p className="hero-message">{heroMessage}</p>
        <div className="hero-actions">
          <Link to="/upload" className="hero-btn white">{"📄"} Upload Syllabus</Link>
          <Link to="/calendar" className="hero-btn ghost">{"📅"} View Calendar</Link>
          {isStaff && <Link to="/admin" className="hero-btn ghost">{"⚙️"} Admin Panel</Link>}
        </div>
      </div>

      <div className="stats-grid">
        {stats.map((s, i) => (
          <div className="stat-card" key={i}>
            <div className={`stat-icon ${s.color}`}>{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: "var(--space-xl)" }}>
        <div className="quick-actions">
          <Link to="/upload" className="quick-action-btn primary">+ Upload Syllabus</Link>
          <Link to="/templates" className="quick-action-btn">{"📚"} Course Templates</Link>
          <Link to="/calendar" className="quick-action-btn">{"📅"} Weekly Calendar</Link>
          <Link to="/profile" className="quick-action-btn">{"👤"} My Profile</Link>
          {isStaff && <Link to="/admin" className="quick-action-btn">{"⚙️"} Admin Panel</Link>}
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Upcoming Tasks</h3>
            <span className="card-badge">{pendingTasks.length} pending</span>
          </div>
          {loading ? (
            <div className="empty-state"><p className="empty-state-text">Loading tasks...</p></div>
          ) : pendingTasks.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">{"🎉"}</div>
              <p className="empty-state-text">No pending tasks — upload a syllabus to get started.</p>
            </div>
          ) : (
            <ul className="task-list">
              {pendingTasks.map((t) => {
                const tag = taskTag(t.due_date);
                return (
                  <li className="task-item" key={t.id}>
                    <div className="task-checkbox" />
                    <div className="task-info">
                      <div className="task-name">{t.course_code ? `${t.course_code} — ` : ""}{t.title}</div>
                      <div className="task-meta">{formatDue(t.due_date)}</div>
                    </div>
                    <span className={`task-tag ${tag.cls}`}>{tag.label}</span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Reminders</h3>
            <span className="card-badge">{reminders.length} active</span>
          </div>
          {reminders.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">{"🔔"}</div>
              <p className="empty-state-text">No active reminders.</p>
            </div>
          ) : (
            <div className="reminder-list">
              {reminders.slice(0, 6).map((r) => (
                <div className="reminder-item" key={r.id}>
                  <div className="reminder-dot blue" />
                  <div style={{ flex: 1 }}>
                    <div className="reminder-text">{r.title}</div>
                    <div className="reminder-time">
                      {new Date(r.remind_at).toLocaleString([], { weekday: "short", hour: "numeric", minute: "2-digit" })}
                    </div>
                  </div>
                  <button
                    onClick={() => dismissReminder(r.id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--color-text-muted)",
                      cursor: "pointer",
                      fontSize: "1rem",
                    }}
                    title="Dismiss"
                  >
                    {"✕"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Today's Schedule</h3>
            <span className="card-badge">{todaySchedule.length} tasks</span>
          </div>
          {todaySchedule.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state-text">Nothing scheduled for today.</p>
            </div>
          ) : (
            todaySchedule.map((s, i) => (
              <div className="schedule-item" key={s.id || i}>
                <span className="schedule-time">
                  {s.scheduled_start
                    ? new Date(s.scheduled_start).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })
                    : "All day"}
                </span>
                <div className="schedule-bar blue" />
                <div className="schedule-details">
                  <div className="schedule-name">{s.course_code ? `${s.course_code} — ` : ""}{s.title}</div>
                  <div className="schedule-location">{s.duration_minutes} min</div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="card">
          <MiniCalendar eventDates={tasks.map((t) => t.due_date).filter(Boolean)} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
