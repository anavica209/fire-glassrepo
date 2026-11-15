"""SQLAlchemy Core with async connections pool"""
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

section_time_events = Table(
    "section_time_events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_key", Text, nullable=False),
    Column("username", Text, nullable=False),
    Column("section", Integer, nullable=False),
    Column("duration_seconds", Float, nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    CheckConstraint("section BETWEEN 1 AND 5", name="section_range"),
)
