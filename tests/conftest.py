from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from partner_os_v2.config import Settings, get_settings
from partner_os_v2.db import get_session_factory, init_db, reset_db_state
from partner_os_v2.services.auth import ensure_admin_user


@pytest.fixture
def db_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Session, Settings]:
    db_path = tmp_path / "unit.db"
    monkeypatch.setenv("PARTNER_OS_V2_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("PARTNER_OS_V2_TOKEN_SECRET", "test-secret")
    monkeypatch.setenv("PARTNER_OS_V2_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("PARTNER_OS_V2_ADMIN_PASSWORD", "admin123")
    monkeypatch.setenv("PARTNER_OS_V2_AI_MODE", "mock")
    monkeypatch.setenv("PARTNER_OS_V2_REQUIRE_AI_RECOMMENDATION", "true")

    get_settings.cache_clear()
    reset_db_state()
    settings = get_settings()

    init_db()
    session_factory = get_session_factory()
    db = session_factory()
    ensure_admin_user(db, settings)

    try:
        yield db, settings
    finally:
        db.close()
