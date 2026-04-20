"""
ORM schema for imported resources
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.records import Record


class ImportedResource(Base):
    """
    Model representing original raw imported resources
    """

    __tablename__ = "imported_resources"

    # Attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    raw_body: Mapped[list] = mapped_column(Text, nullable=False, server_default="")
    validation_errors: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Foreign keys
    record_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("records.id"),
        nullable=True,
    )

    # Relationships
    record: Mapped["Record"] = relationship(
        "Record", back_populates="imported_resource"
    )
