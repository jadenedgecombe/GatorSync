"""Test that the db-check endpoint works when a database is available.

This test is skipped if PostgreSQL is not reachable — it will pass in CI
once the database service is configured, and locally once PostgreSQL is running.
"""

import pytest
from sqlalchemy import text

from app.database import engine


def _db_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_is_reachable(), reason="PostgreSQL not running")
def test_db_check(client):
    response = client.get("/api/db-check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert data["database"] == "PostgreSQL"
    assert isinstance(data["roles"], list)
