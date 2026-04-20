import json
from app.config import ExtractionConfig
from app.models.records import Record

config = ExtractionConfig.model_validate({
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
})

with open("tmp/missing_data.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        data = json.loads(line)
        record = Record.from_data(data, config)
        print(record.resource_type, record.id, record.code, record.subject)
