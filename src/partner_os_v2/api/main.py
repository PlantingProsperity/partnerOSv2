"""FastAPI entrypoint for Partner OS v2."""

from __future__ import annotations

from fastapi import FastAPI

from partner_os_v2.api.routes.ai import router as ai_router
from partner_os_v2.api.routes.analyses import router as analyses_router
from partner_os_v2.api.routes.auth import router as auth_router
from partner_os_v2.api.routes.cases import router as cases_router
from partner_os_v2.api.routes.deals import router as deals_router
from partner_os_v2.api.routes.documents import router as documents_router
from partner_os_v2.api.routes.health import router as health_router
from partner_os_v2.api.routes.leads import router as leads_router
from partner_os_v2.api.routes.timeline import router as timeline_router
from partner_os_v2.config import get_settings
from partner_os_v2.db import get_session_factory, init_db
from partner_os_v2.services.auth import ensure_admin_user

app = FastAPI(title="Partner OS v2 API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    session_factory = get_session_factory()
    with session_factory() as db:
        ensure_admin_user(db, get_settings())


app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(leads_router)
app.include_router(analyses_router)
app.include_router(deals_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(timeline_router)
app.include_router(health_router)
