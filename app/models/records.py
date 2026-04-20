"""
ORM schema for records
"""

from datetime import datetime
from typing import Dict, List, TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
from app.config import ExtractionConfig, ExtractableResources
from app.utils.dict import normalize_keys
from app.requests.transform import TransformationCriteria
from app.transformations.schema import ACTION_MAPPING


if TYPE_CHECKING:
    from app.models.imported_resources import ImportedResource

DEFAULT_TRANSFORMATIONS = [
    {
        "action": "extract",
        "field": "component[0].code",
        "as": "code",
    },
    {
        "action": "extract",
        "field": "component[0].valueQuantity",
        "as": "valueQuantity",
    },
    {
        "action": "extract",
        "field": "code.coding[0].code",
        "as": "code",
    },
    {
        "action": "extract",
        "field": "valueQuantity.value",
        "as": "valueQuantity",
    },
    {
        "action": "extract",
        "field": "subject.reference",
        "as": "subject",
    },
]


class Record(Base):
    __tablename__ = "records"

    # Attributes
    id: Mapped[str] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(255), nullable=False)

    # Only Observations
    effective_date_time: Mapped[str] = mapped_column(String(255), nullable=True)
    value_quantity: Mapped[str] = mapped_column(String(255), nullable=True)

    # Only Procedures
    performed_date_time: Mapped[str] = mapped_column(String(255), nullable=True)

    # Only MedicationRequest
    dosage_instruction: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(255), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    imported_resource: Mapped["ImportedResource"] = relationship(
        "ImportedResource", back_populates="record"
    )

    def values(self, fields: List[str] | None = None):
        """
        Get all values as dict

        Returns:
            dict: Dictionary with all values
        """
        if fields is None:
            fields = [c.name for c in self.__table__.columns]

        return {column_name: getattr(self, column_name) for column_name in fields}

    @classmethod
    def from_data(
        cls,
        data: dict,
        config: ExtractionConfig | None = None,
        transformations: List[Dict] | None = None,
    ):
        # Apply transformations
        transformations = transformations or DEFAULT_TRANSFORMATIONS
        for t in transformations:
            transformation = TransformationCriteria(**t)
            action = ACTION_MAPPING[transformation.action]
            data = action(data, transformation.field, transformation.as_field)

        # Use configured fields
        data = {
            key: data.get(key)
            for key, configured_setting in config.fields
            if configured_setting == ExtractableResources.ALL
            or data.get("resourceType", data.get("resource_type")) in map(lambda c: c.value, configured_setting)
        }
        data = normalize_keys(data)

        return cls(**data)
