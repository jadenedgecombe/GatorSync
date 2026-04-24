"""Syllabus parser — extracts assignment rows from PDF/DOCX text.

Strategy: multi-pass. Each line is routed through specialized handlers in order,
falling back to a generic date-line handler. Lines that look like bibliographic
citations, office hours, URLs, or staff directory entries are filtered out
before any date parsing happens.

Handlers (in priority order):
  1. Junk filter — skips textbook citations, office hours, URLs, headings.
  2. Week-row handler — "Week N M/D - M/D Topic" (course schedule tables).
  3. Prose-deadline handler — "X is due on Y".
  4. Generic date-line handler — any other line containing a date.
"""

from __future__ import annotations

import io
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Iterable

from dateutil import parser as dateutil_parser
from docx import Document
from pypdf import PdfReader


# ---- Type classification ----------------------------------------------------

# Ordered by specificity — more specific patterns win over generic ones.
# Each entry: (type, list of lowercase keywords/phrases).
TYPE_KEYWORDS_ORDERED: list[tuple[str, list[str]]] = [
    ("project", ["sprint", "presentation week", "open-source project", "open source project",
                  "team project", "capstone project", "final project", "mini project"]),
    ("exam", ["midterm exam", "final exam", "exam on ", " midterm ", " midterm.", "midterm,"]),
    ("project", ["project", "capstone"]),
    ("quiz", ["quiz"]),
    ("reading", ["reading", "chapter", "read chapter"]),
    ("homework", ["homework", "hw ", " hw,", "hw:", "assignment", "problem set",
                   "pset", "deliverable", "write-up", "writeup"]),
]

TYPE_HOURS = {
    "exam": 6,
    "project": 8,
    "quiz": 1,
    "reading": 2,
    "homework": 3,
    "other": 2,
}


def _classify_topic(text: str, for_week_row: bool = False) -> str:
    """Classify an assignment text into our type enum.

    When `for_week_row=True`, the generic "project" keyword is de-weighted so
    that a lecture topic like "Project and risk management" isn't classified
    as a project deliverable.
    """
    low = f" {text.lower()} "

    for atype, keywords in TYPE_KEYWORDS_ORDERED:
        if atype == "project" and keywords == ["project", "capstone"] and for_week_row:
            continue
        if any(k in low for k in keywords):
            return atype

    return "reading" if for_week_row else "homework"


def _estimate_hours(atype: str) -> int:
    return TYPE_HOURS.get(atype, 2)


# ---- Date parsing -----------------------------------------------------------

MONTH_NAMES = r"(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)"

DATE_PATTERNS = [
    # ISO: 2026-10-14
    re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"),
    # Slash: 10/14 or 10/14/2026
    re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b"),
    # Month first: "October 14" or "Oct. 14, 2026"
    re.compile(rf"\b{MONTH_NAMES}\.?\s+\d{{1,2}}(?:(?:st|nd|rd|th)\b)?(?:,?\s+\d{{2,4}})?\b", re.IGNORECASE),
    # Day first: "17th February" or "17 February 2026"
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTH_NAMES}(?:,?\s+\d{{2,4}})?\b", re.IGNORECASE),
]


def _find_date(text: str, reference_year: int) -> tuple[date, str] | None:
    """Return (parsed_date, matched_text) for the FIRST date in the text."""
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        candidate = match.group(0)
        try:
            default = datetime(reference_year, 1, 1)
            parsed = dateutil_parser.parse(candidate, default=default, fuzzy=False)
            return parsed.date(), candidate
        except (ValueError, OverflowError):
            continue
    return None


def _find_last_date(text: str, reference_year: int) -> tuple[date, str] | None:
    """Return (parsed_date, matched_text) for the LAST date in the text."""
    best: tuple[date, str] | None = None
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(0)
            try:
                default = datetime(reference_year, 1, 1)
                parsed = dateutil_parser.parse(candidate, default=default, fuzzy=False)
                best = (parsed.date(), candidate)
            except (ValueError, OverflowError):
                continue
    return best


# ---- Junk / noise filtering -------------------------------------------------

JUNK_PATTERNS = [
    re.compile(r"\bISBN[:\s0-9]", re.IGNORECASE),
    re.compile(r"\b(Pearson|Addison[\s-]*Wesley|Springer|Wiley|O'?Reilly|"
               r"McGraw[\s-]*Hill|Oxford|Cambridge|Prentice[\s-]*Hall|MIT Press)\b",
               re.IGNORECASE),
    re.compile(r"\b\d+(?:st|nd|rd|th)\s+edition\b", re.IGNORECASE),
    re.compile(r"@[\w.-]+\.(?:edu|com|org)"),
    re.compile(r"https?://"),
    re.compile(r"\bzoom\.us\b", re.IGNORECASE),
    re.compile(r"^\s*(Instructor|Location|Class\s+Periods?|Office\s+(?:Hours?|location)|"
               r"Email|Peer\s+Mentors?|Academic\s+Term|Room\s+No|MALA)", re.IGNORECASE),
    re.compile(r"^(Name|Day of Week|Time|Office location|Outcome|Coverage)\b", re.IGNORECASE),
    re.compile(r"^(Grade\s+Category|Percentage|Total|Participation|"
               r"Peer\s+Evaluation)\s*\d", re.IGNORECASE),
    re.compile(r"^\s*Page\s+\d", re.IGNORECASE),
    # Lines that are pure phone numbers or office locations
    re.compile(r"^\(?\d{3}\)?[\s-]\d{3}[\s-]\d{4}"),
]

# A line is a "meeting-time" entry if it has a time range but no calendar date.
MEETING_TIME_RE = re.compile(
    r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\s*[–\-−to]+\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?",
)


def _is_junk(line: str, year: int) -> bool:
    """Return True if this line should be skipped before any date parsing."""
    for pat in JUNK_PATTERNS:
        if pat.search(line):
            return True

    # Meeting-time entries without a calendar date (office hours, peer mentor slots)
    if MEETING_TIME_RE.search(line) and not _find_date(line, year):
        return True

    # Pure headings (short, all-caps or title-case with no digits)
    if len(line) < 30 and not any(ch.isdigit() for ch in line):
        # e.g. "Course Description", "Materials and Supply Fees"
        if line.count(" ") <= 5:
            return True

    return False


# ---- Title extraction -------------------------------------------------------

LEADING_MARKER_RE = re.compile(r"^[\s•\-\*•◦·]+")
LEADING_DUE_RE = re.compile(r"^(due|deadline|assigned|released)\s*[:\-]\s*", re.IGNORECASE)
PAREN_HOLIDAY_RE = re.compile(
    r"\s*\((?:\d+(?:st|nd|rd|th)?[\s,]*)*"
    r"(?:spring\s*break|reading\s*day[s]?|holiday|no\s+class|"
    r"dead\s*week|finals?\s*week)[^)]*\)",
    re.IGNORECASE,
)


def _clean_line(line: str) -> str:
    line = LEADING_MARKER_RE.sub("", line)
    line = LEADING_DUE_RE.sub("", line)
    return line.strip()


def _cleanup_title(text: str, *matched_dates: str) -> str:
    for d in matched_dates:
        if d:
            text = text.replace(d, " ")
    text = PAREN_HOLIDAY_RE.sub("", text)
    # Repair pypdf artifacts: "open -source" → "open-source", "class -related" → "class-related"
    text = re.sub(r"(\w)\s+-\s*(\w)", r"\1-\2", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\-:.,()/&?!]", " ", text)
    return text.strip(" -:,.–—")[:250]


# ---- Data class -------------------------------------------------------------


@dataclass
class ParsedRow:
    title: str
    due_date: str | None  # ISO date string
    assignment_type: str
    estimated_hours: int
    raw_line: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---- Specialized handlers ---------------------------------------------------

# "Week 2  1/19 – 1/23  (19th Holiday)  Software activities and process model"
WEEK_ROW_RE = re.compile(
    r"^Week\s+(\d+)\s+"
    r"(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s*[–\-−]\s*"
    r"(\d{1,2}/\d{1,2}(?:/\d{2,4})?)"
    r"\s*(.*)$",
    re.IGNORECASE,
)


def _try_week_row(line: str, year: int) -> ParsedRow | None:
    m = WEEK_ROW_RE.match(line)
    if not m:
        return None
    week_num, start_str, end_str, topic = m.groups()

    # Parse end-of-week as the default due date; assignments are due at end of week.
    end_date = _find_date(end_str, year)
    start_date = _find_date(start_str, year)
    due = (end_date or start_date)
    if not due:
        return None
    due_date, _ = due

    topic = topic.strip()
    if re.search(r"spring\s*break", topic, re.IGNORECASE):
        return None  # Skip break weeks entirely

    atype = _classify_topic(topic, for_week_row=True)
    cleaned_topic = _cleanup_title(topic)

    title = f"Week {week_num}: {cleaned_topic}" if cleaned_topic else f"Week {week_num}"
    return ParsedRow(
        title=title[:250],
        due_date=due_date.isoformat(),
        assignment_type=atype,
        estimated_hours=_estimate_hours(atype),
        raw_line=line,
    )


# "The open-source project is due on 17th February."
PROSE_DEADLINE_RE = re.compile(
    r"(?i)([^.]{3,120}?)\s+(?:is|are|will\s+be)?\s*due\s+(?:on|by|before)?\s*([^.]+)"
)


def _try_prose_deadline(line: str, year: int) -> ParsedRow | None:
    for match in PROSE_DEADLINE_RE.finditer(line):
        subject, date_part = match.groups()
        hit = _find_date(date_part, year)
        if not hit:
            continue
        parsed_date, raw = hit

        subject = _clean_line(subject)
        subject = re.sub(r"^(the|a|an|all|some|your)\s+", "", subject, flags=re.IGNORECASE)
        subject = _cleanup_title(subject)
        subject = subject.title() if subject.islower() else subject
        subject = subject.rstrip(",;: –—")
        if len(subject) < 3:
            continue

        # Ignore generic framings like "All assignments will be due on Tuesday of each week"
        if re.search(r"\b(each|every|all)\b", subject, re.IGNORECASE):
            continue
        if "tuesday" in date_part.lower() and "each week" in line.lower():
            continue

        atype = _classify_topic(subject)
        return ParsedRow(
            title=subject[:250],
            due_date=parsed_date.isoformat(),
            assignment_type=atype,
            estimated_hours=_estimate_hours(atype),
            raw_line=line,
        )
    return None


def _try_generic_date_line(line: str, year: int) -> ParsedRow | None:
    hit = _find_date(line, year)
    if not hit:
        return None
    parsed_date, raw = hit

    title = _cleanup_title(line, raw)
    if len(title) < 3:
        return None

    atype = _classify_topic(title)
    return ParsedRow(
        title=title,
        due_date=parsed_date.isoformat(),
        assignment_type=atype,
        estimated_hours=_estimate_hours(atype),
        raw_line=line,
    )


# ---- File extraction -------------------------------------------------------


def extract_text_from_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def extract_text_from_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(data)
    if lower.endswith(".docx"):
        return extract_text_from_docx(data)
    if lower.endswith(".txt"):
        return data.decode("utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {filename}")


# ---- Main entrypoint --------------------------------------------------------


def parse_syllabus_text(text: str, reference_year: int | None = None) -> list[ParsedRow]:
    year = reference_year or datetime.now().year
    # A loose "sanity window" — treat dates much earlier than the academic year as citations.
    min_year = year - 1
    max_year = year + 2

    rows: list[ParsedRow] = []
    seen: set[tuple[str, str | None]] = set()

    for raw in text.splitlines():
        line = _clean_line(raw)
        if len(line) < 6:
            continue
        if _is_junk(line, year):
            continue

        # If this looks like a course schedule row, only use the week handler.
        # Returning None from that handler (e.g. Spring Break) means "skip line".
        if WEEK_ROW_RE.match(line):
            row = _try_week_row(line, year)
            if not row:
                continue
        else:
            row = _try_prose_deadline(line, year) or _try_generic_date_line(line, year)

        if not row or not row.due_date:
            continue

        # Drop dates outside the reasonable window (textbook publication dates, etc.)
        try:
            parsed = date.fromisoformat(row.due_date)
            if parsed.year < min_year or parsed.year > max_year:
                continue
        except ValueError:
            continue

        key = (row.title.lower(), row.due_date)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)

    return rows


def parse_file(filename: str, data: bytes, reference_year: int | None = None) -> list[dict]:
    text = extract_text(filename, data)
    rows = parse_syllabus_text(text, reference_year=reference_year)
    return [r.to_dict() for r in rows]


def dedupe_by_title(rows: Iterable[dict]) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for r in rows:
        key = r["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
