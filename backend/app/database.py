import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

database_url = settings.database_url

# Normalize common provider URLs (Supabase/Railway give postgres://...) to a
# SQLAlchemy URL with an explicit driver.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"connect_timeout": 15}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema() -> None:
    """Create tables and add missing columns (lightweight auto-migration)."""
    Base.metadata.create_all(bind=engine)
    insp = sa.inspect(engine)
    if "profiles" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("profiles")}
        if "is_id_verified" not in cols:
            with engine.begin() as conn:
                conn.execute(sa.text(
                    "ALTER TABLE profiles ADD COLUMN is_id_verified BOOLEAN NOT NULL DEFAULT FALSE"
                ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
