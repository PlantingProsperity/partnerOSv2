from __future__ import annotations

import anyio

from partner_os_v2.api.main import app


def test_app_startup_shutdown_smoke():
    async def run() -> None:
        await app.router.startup()
        await app.router.shutdown()

    anyio.run(run)
