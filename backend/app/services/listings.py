"""Bulk insert listings into listing_master using the shared SQLAlchemy session."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import ListingMaster
from app.schemas import ListingCreate


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def bulk_insert_listings(db: Session, listings: list[ListingCreate]) -> int:
    if not listings:
        raise ValueError("Cannot insert an empty listings payload.")

    rows = [
        ListingMaster(
            business_name=item.business_name.strip(),
            category=_optional_text(item.category),
            city=_optional_text(item.city),
            address=_optional_text(item.address),
            phone=_optional_text(item.phone),
            source=_optional_text(item.source),
        )
        for item in listings
    ]

    try:
        db.add_all(rows)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return len(rows)
