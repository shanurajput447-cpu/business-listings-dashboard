from datetime import datetime

from sqlalchemy import Index, String, Text, func
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ListingMaster(Base):
    """Maps to the listing_master table. Insert and query logic will be added later."""

    __tablename__ = "listing_master"
    __table_args__ = (
        Index("idx_listing_master_city", "city"),
        Index("idx_listing_master_category", "category"),
        Index("idx_listing_master_source", "source"),
    )

    id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), primary_key=True, autoincrement=True
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(150), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
