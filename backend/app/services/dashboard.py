"""SQL aggregations over listing_master for dashboard endpoints."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

UNKNOWN_GROUP_LABEL = "Unknown"


def _grouped_count_statement(column: ColumnElement[str | None], label: str) -> Select:
    grouped = func.coalesce(func.nullif(func.trim(column), ""), UNKNOWN_GROUP_LABEL)
    count_col = func.count().label("count")
    return (
        select(grouped.label(label), count_col)
        .group_by(grouped)
        .order_by(count_col.desc(), grouped.asc())
    )


def _rows_to_counts(db: Session, column: ColumnElement[str | None], label: str) -> list[dict[str, str | int]]:
    rows = db.execute(_grouped_count_statement(column, label)).all()
    return [{label: str(row[0]), "count": int(row[1])} for row in rows]


def get_city_counts(db: Session) -> list[dict[str, str | int]]:
    from app.models import ListingMaster

    return _rows_to_counts(db, ListingMaster.city, "city")


def get_category_counts(db: Session) -> list[dict[str, str | int]]:
    from app.models import ListingMaster

    return _rows_to_counts(db, ListingMaster.category, "category")


def get_source_counts(db: Session) -> list[dict[str, str | int]]:
    from app.models import ListingMaster

    return _rows_to_counts(db, ListingMaster.source, "source")
