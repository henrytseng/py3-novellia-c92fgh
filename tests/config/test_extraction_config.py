from app.config import ExtractionConfig


def test_valid_extraction_config():
    """
    Test valid configuration does not raise errors
    """
    ExtractionConfig.model_validate(
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
