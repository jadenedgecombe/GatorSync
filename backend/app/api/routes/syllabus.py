"""Syllabus parse + bulk import routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.routes.assignments import _autogenerate_tasks
from app.auth import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.user import User
from app.services.syllabus_parser import parse_file

router = APIRouter()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class ParsedRowOut(BaseModel):
    title: str
    due_date: str | None
    assignment_type: str
    estimated_hours: int
    raw_line: str


class ParseResponse(BaseModel):
    filename: str
    rows: list[ParsedRowOut]


class ImportRow(BaseModel):
    title: str
    due_date: datetime | None = None
    assignment_type: str = "homework"
    estimated_hours: int = 2


class ImportRequest(BaseModel):
    course_id: str
    rows: list[ImportRow]


class ImportResponse(BaseModel):
    course_id: str
    created_count: int


@router.post("/parse", response_model=ParseResponse)
async def parse_syllabus(
    file: UploadFile = File(...),
    reference_year: int | None = Form(None),
    _current_user: User = Depends(get_current_user),
):
    name_lower = (file.filename or "").lower()
    ext = next((e for e in ALLOWED_EXTENSIONS if name_lower.endswith(e)), None)
    if not ext:
        raise HTTPException(status_code=415, detail="Only PDF, DOCX, and TXT are supported")

    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    try:
        rows = parse_file(file.filename, data, reference_year=reference_year)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse: {exc}")

    return ParseResponse(filename=file.filename, rows=rows)


@router.post("/import", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
def import_parsed_rows(
    body: ImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cid = uuid.UUID(body.course_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Course not found")

    course = db.query(Course).filter(Course.id == cid).first()
    if not course or course.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Course not found")

    created = 0
    for row in body.rows:
        a = Assignment(
            course_id=cid,
            title=row.title,
            due_date=row.due_date,
            assignment_type=row.assignment_type,
            estimated_hours=row.estimated_hours,
        )
        db.add(a)
        db.flush()
        _autogenerate_tasks(a, db)
        created += 1

    db.commit()
    return ImportResponse(course_id=body.course_id, created_count=created)
