import pytest
import os

from sqlalchemy import create_engine

from app.config import ExtractionConfig
from app.models.records import Record  # noqa
from app.models.imported_resources import ImportedResource  # noqa


@pytest.fixture
def db_engine():
    db_url = os.getenv("TEST_DATABASE_URI")
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture
def sample_config():
    return ExtractionConfig.model_validate(
        {
            "fields": {
                "id": "all",
                "subject": "all",
                "code": "all",
                "resourceType": "all",
                "effectiveDateTime": ["Observation"],
                "performedDateTime": ["Procedure"],
                "dosageInstruction": ["MedicationRequest"],
                "valueQuantity": ["Observation"],
                "status": [
                    "Observation",
                    "Procedure",
                    "Condition",
                    "MedicationRequest",
                ],
            }
        }
    )
