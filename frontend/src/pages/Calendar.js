import React from "react";

const events = [
  { time: "9:00 AM", name: "COP 3530 — Data Structures", location: "CSE E121", color: "blue" },
  { time: "11:00 AM", name: "CDA 3101 — Computer Organization", location: "NEB 202", color: "green" },
  { time: "1:00 PM", name: "ENC 3246 — Professional Writing", location: "TUR 2322", color: "orange" },
  { time: "2:00 PM", name: "Office Hours — Prof. Davis", location: "CSE 404", color: "red" },
  { time: "3:30 PM", name: "CEN 3031 — Software Engineering", location: "CSE E116", color: "blue" },
  { time: "5:30 PM", name: "Study Group — Data Structures", location: "Library West 312", color: "green" },
];

function Calendar() {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Calendar</h1>
        <p className="page-subtitle">{today}</p>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Today's Schedule</h3>
            <span className="card-badge">{events.length} events</span>
          </div>
          {events.map((e, i) => (
            <div className="schedule-item" key={i}>
              <span className="schedule-time">{e.time}</span>
              <div className={`schedule-bar ${e.color}`} />
              <div className="schedule-details">
                <div className="schedule-name">{e.name}</div>
                <div className="schedule-location">{e.location}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Coming Up This Week</h3>
          </div>
          <ul className="task-list">
            <li className="task-item">
              <div className="task-checkbox" />
              <div className="task-info">
                <div className="task-name">CDA 3101 — Homework 5</div>
                <div className="task-meta">Due Tomorrow, 11:59 PM</div>
              </div>
              <span className="task-tag urgent">Urgent</span>
            </li>
            <li className="task-item">
              <div className="task-checkbox" />
              <div className="task-info">
                <div className="task-name">COP 3530 — Project 2 Report</div>
                <div className="task-meta">Due Friday, Mar 28</div>
              </div>
              <span className="task-tag soon">Soon</span>
            </li>
            <li className="task-item">
              <div className="task-checkbox" />
              <div className="task-info">
                <div className="task-name">ENC 3246 — Peer Review Draft</div>
                <div className="task-meta">Due Sunday, Mar 30</div>
              </div>
              <span className="task-tag normal">Upcoming</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Calendar;
