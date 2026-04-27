import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiSend, API_URL } from "../api";

const BUCKET_CLASS = {
  empty: "heatmap-empty",
  light: "heatmap-light",
  medium: "heatmap-medium",
  heavy: "heatmap-heavy",
};

function mondayOf(date) {
  const d = new Date(date);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

// Build YYYY-MM-DD from local date components so we don't get shifted
// into UTC (which, in US timezones, drops the date by one day).
function formatISODate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

// Parse "YYYY-MM-DD" as a LOCAL-midnight date (not UTC midnight).
// Using `new Date("2026-04-20")` would parse as UTC → display in ET as Apr 19.
function parseLocalDate(iso) {
  const [y, m, day] = iso.split("-").map(Number);
  return new Date(y, m - 1, day);
}

function dayLabel(iso) {
  return parseLocalDate(iso).toLocaleDateString([], {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function Calendar() {
  const { user, token } = useAuth();
  const [weekStart, setWeekStart] = useState(() => mondayOf(new Date()));
  const [week, setWeek] = useState(null);
  const [heatmap, setHeatmap] = useState([]);
  const [overload, setOverload] = useState(null);
  const [draggingTaskId, setDraggingTaskId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const weekStartIso = useMemo(() => formatISODate(weekStart), [weekStart]);
  const todayIso = useMemo(() => formatISODate(new Date()), []);

  const loadWeek = useCallback(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      apiGet(`/schedule/week?start=${weekStartIso}`, token),
      apiGet(`/schedule/heatmap?start=${weekStartIso}&days=7`, token),
      apiGet(`/schedule/overload?date=${todayIso}`, token),
    ])
      .then(([w, h, o]) => {
        setWeek(w);
        setHeatmap(h.days);
        setOverload(o);
        setError("");
      })
      .catch((e) => setError(e.message || "Failed to load schedule"))
      .finally(() => setLoading(false));
  }, [token, weekStartIso, todayIso]);

  useEffect(() => {
    loadWeek();
  }, [loadWeek]);

  const shiftWeek = (days) => {
    const next = new Date(weekStart);
    next.setDate(next.getDate() + days);
    setWeekStart(mondayOf(next));
  };

  const onDragStart = (taskId) => (e) => {
    setDraggingTaskId(taskId);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", taskId);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const onDrop = (targetDateIso) => async (e) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData("text/plain") || draggingTaskId;
    if (!taskId) return;

    const task = week?.days.flatMap((d) => d.tasks).find((t) => t.id === taskId);
    if (!task) return;

    const sourceDate = task.scheduled_start
      ? formatISODate(new Date(task.scheduled_start))
      : task.due_date
      ? formatISODate(new Date(task.due_date))
      : null;
    if (sourceDate === targetDateIso) {
      setDraggingTaskId(null);
      return;
    }

    const [y, m, d] = targetDateIso.split("-").map(Number);
    const newStart = new Date(Date.UTC(y, m - 1, d, 14, 0, 0));
    const newEnd = new Date(newStart.getTime() + (task.duration_minutes || 60) * 60 * 1000);

    try {
      await apiSend(
        `/tasks/${taskId}`,
        "PATCH",
        {
          scheduled_start: newStart.toISOString(),
          scheduled_end: newEnd.toISOString(),
        },
        token
      );
      loadWeek();
    } catch (err) {
      setError(err.message || "Failed to reschedule task");
    } finally {
      setDraggingTaskId(null);
    }
  };

  const toggleComplete = async (task) => {
    try {
      await apiSend(`/tasks/${task.id}`, "PATCH", { is_completed: !task.is_completed }, token);
      loadWeek();
    } catch (err) {
      setError(err.message);
    }
  };

  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  const bucketForDate = (isoDate) => {
    const cell = heatmap.find((c) => c.date === isoDate);
    return cell ? cell.bucket : "empty";
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">{user?.display_name?.split(" ")[0] || "Your"}'s Calendar</h1>
        <p className="page-subtitle">{today}</p>
      </div>

      {error && (
        <div className="error-banner">{error}</div>
      )}

      {overload?.is_overloaded && (
        <div className="overload-banner">
          {"⚠️"} Today's workload is <strong>{Math.round(overload.minutes / 60)} hours</strong>
          {" — "}consider rescheduling some tasks.
        </div>
      )}

      <div className="week-controls">
        <button className="quick-action-btn" onClick={() => shiftWeek(-7)} aria-label="Previous week">{"←"} Prev Week</button>
        <span className="week-range" aria-live="polite">
          Week of {weekStart.toLocaleDateString([], { month: "short", day: "numeric" })}
        </span>
        <button className="quick-action-btn" onClick={() => shiftWeek(7)} aria-label="Next week">Next Week {"→"}</button>
        <button className="quick-action-btn" onClick={() => setWeekStart(mondayOf(new Date()))}>Today</button>
        <a
          href={`${API_URL}/schedule/export.ics?days=30`}
          download="gatorsync.ics"
          className="quick-action-btn"
          aria-label="Export calendar as iCal file"
          style={{ textDecoration: "none" }}
        >
          {"📅"} Export iCal
        </a>
      </div>

      <div className="heatmap-legend">
        <span className="heatmap-cell heatmap-empty" /> None
        <span className="heatmap-cell heatmap-light" /> Light (&lt;3h)
        <span className="heatmap-cell heatmap-medium" /> Medium (3–6h)
        <span className="heatmap-cell heatmap-heavy" /> Heavy (6h+)
      </div>

      {loading && !week ? (
        <div className="empty-state"><p className="empty-state-text">Loading schedule...</p></div>
      ) : (
        <div className="week-grid">
          {week?.days.map((day) => {
            const bucket = bucketForDate(day.date);
            const isToday = day.date === todayIso;
            return (
              <div
                key={day.date}
                className={`week-col ${BUCKET_CLASS[bucket]} ${isToday ? "week-col-today" : ""}`}
                onDragOver={onDragOver}
                onDrop={onDrop(day.date)}
                role="region"
                aria-label={`${dayLabel(day.date)}${isToday ? " (today)" : ""}`}
              >
                <div className="week-col-header">
                  <div className="week-col-day">{dayLabel(day.date)}</div>
                  <div className="week-col-minutes" aria-label={`${Math.round(day.total_minutes / 60 * 10) / 10} hours scheduled`}>{Math.round(day.total_minutes / 60 * 10) / 10}h</div>
                </div>
                {day.tasks.length === 0 ? (
                  <div className="week-col-empty" aria-label="No tasks">—</div>
                ) : (
                  day.tasks.map((t) => (
                    <div
                      key={t.id}
                      className={`week-task ${t.is_completed ? "completed" : ""}`}
                      draggable
                      onDragStart={onDragStart(t.id)}
                      title="Drag to reschedule"
                      role="article"
                      aria-label={`${t.title}${t.is_completed ? " (completed)" : ""}`}
                    >
                      <div className="week-task-row">
                        <input
                          type="checkbox"
                          checked={t.is_completed}
                          onChange={() => toggleComplete(t)}
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`Mark "${t.title}" as ${t.is_completed ? "incomplete" : "complete"}`}
                        />
                        <div className="week-task-title">
                          {t.course_code ? `${t.course_code}` : ""}
                        </div>
                      </div>
                      <div className="week-task-name">{t.title}</div>
                      <div className="week-task-time">
                        {t.scheduled_start ? formatTime(t.scheduled_start) : formatTime(t.due_date)}
                        {" · "}{t.duration_minutes} min
                      </div>
                    </div>
                  ))
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Calendar;
