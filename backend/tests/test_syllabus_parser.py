"""Parser unit tests (no DB required)."""

from app.services.syllabus_parser import parse_syllabus_text


SAMPLE = """
COP 3530 — Data Structures
Spring 2026

Homework 1 — Due January 28
HW 2: Array operations — 02/11/2026
Project 1 Milestone 1: Proposal - Feb 18, 2026
Midterm Exam on March 10
Reading: Chapter 5 by 3/15
Final Project due 4/20/2026
"""


def test_parses_varied_date_formats():
    rows = parse_syllabus_text(SAMPLE, reference_year=2026)
    titles = [r.title for r in rows]

    assert any("Homework 1" in t for t in titles)
    assert any("HW 2" in t for t in titles)
    assert any("Midterm" in t for t in titles)
    assert any("Final Project" in t for t in titles)


def test_classifies_assignment_types():
    rows = parse_syllabus_text(SAMPLE, reference_year=2026)
    by_title = {r.title: r for r in rows}

    midterm = next(r for t, r in by_title.items() if "Midterm" in t)
    assert midterm.assignment_type == "exam"

    project = next(r for t, r in by_title.items() if "Final Project" in t)
    assert project.assignment_type == "project"

    reading = next(r for t, r in by_title.items() if "Chapter" in t or "Reading" in t)
    assert reading.assignment_type == "reading"


def test_returns_iso_dates():
    rows = parse_syllabus_text(SAMPLE, reference_year=2026)
    for r in rows:
        assert r.due_date is not None
        assert len(r.due_date) == 10  # YYYY-MM-DD


def test_empty_input_returns_empty_list():
    assert parse_syllabus_text("", reference_year=2026) == []


def test_skips_lines_without_dates():
    text = "COP 3530 — Data Structures\nInstructor: Prof. Davis\nOffice: CSE 404\n"
    assert parse_syllabus_text(text, reference_year=2026) == []


# --- Real-world syllabus format (CEN 3031-style) ---

REAL_SYLLABUS = """
Introduction to Software Engineering CEN 3031
Instructor: Neha Rani, PhD
neharani@ufl.edu
Office Hours: W 3:15 pm-4:15 pm

Required:
• Engineering Software Products
• Pearson; 1st edition (May 19, 2019)
• ISBN 9780135211168

Recommended:
• Essential Scrum
• Addison-Wesley Professional; 1st edition (July 26, 2012)
• ISBN: 9780137043293

Course Schedule
Week 1  1/12 - 1/16 Introduction and course overview, What is Software Engineering?
Week 2  1/19 – 1/23 (19th Holiday) Software activities and process model
Week 7  2/23 – 2/27 Presentation week
Week 8  3/2 – 3/6 Sprint 1 Software architecture models
Week 10 3/16 – 3/20 (Spring break)
Week 15 4/20 – 4/24 (23rd, 24th reading days) Presentation Week

All assignments will be due on Tuesday of each week.
The open-source project is due on 17th February.
"""


def test_filters_textbook_citations():
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    titles = " | ".join(r.title for r in rows)
    assert "Pearson" not in titles
    assert "Addison" not in titles
    assert "ISBN" not in titles


def test_skips_spring_break_week():
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    weeks = [r.title for r in rows if "Week 10" in r.title]
    assert weeks == []


def test_classifies_sprint_weeks_as_projects():
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    sprint = next(r for r in rows if "Sprint 1" in r.title)
    assert sprint.assignment_type == "project"


def test_classifies_presentation_weeks_as_projects():
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    pres = [r for r in rows if "Presentation" in r.title]
    assert len(pres) >= 2
    for r in pres:
        assert r.assignment_type == "project"


def test_lecture_topics_classify_as_reading():
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    week1 = next(r for r in rows if r.title.startswith("Week 1:"))
    assert week1.assignment_type == "reading"


def test_captures_prose_deadline_day_first():
    """The open-source project is due on 17th February — verify day-first date parsing."""
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    osp = next((r for r in rows if "Open-Source" in r.title or "open-source" in r.title.lower()), None)
    assert osp is not None
    assert osp.due_date == "2026-02-17"
    assert osp.assignment_type == "project"


def test_ignores_generic_due_statements():
    """'All assignments will be due on Tuesday of each week' should not produce a row."""
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    for r in rows:
        assert "each week" not in r.title.lower()
        assert "all assignments" not in r.title.lower()


def test_week_due_date_uses_end_of_week():
    """Week 1 spans 1/12 - 1/16 — due date should be the end (1/16)."""
    rows = parse_syllabus_text(REAL_SYLLABUS, reference_year=2026)
    week1 = next(r for r in rows if r.title.startswith("Week 1:"))
    assert week1.due_date == "2026-01-16"
