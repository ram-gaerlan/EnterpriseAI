"""One-off script to create all tables defined in our models.

This is a deliberate simplification for Phase 1. Real production systems use a
migration tool like Alembic to version schema changes over time — create_all()
works fine for a fresh project, but it can't handle altering existing tables.
We'll flag Alembic as a future improvement in the README.
"""
import asyncio

from app.database import Base, engine
from app.models import db_models  # noqa: F401 — import registers models with Base.metadata


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())