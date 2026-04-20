from app.models.records import Record


def test_record_from_data(sample_config, db_engine):
    data = {"id": "1", "subject": "1", "code": "1", "resourceType": "1"}
    record = Record.from_data(data, sample_config)
    assert record.id == "1"
    assert record.subject == "1"
    assert record.code == "1"
    assert record.resource_type == "1"


def test_record_with_nested_code(sample_config, db_engine):
    data = {
        "id": "1",
        "subject": "1",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel",
                }
            ],
            "text": "Blood Pressure",
        },
        "resourceType": "1",
    }
    record = Record.from_data(data, sample_config)
    assert record.id == "1"
    assert record.code == "85354-9"


def test_record_with_nested_value_quantity(sample_config, db_engine):
    data = {
        "id": "1",
        "subject": "1",
        "valueQuantity": {
            "value": "120",
            "unit": "mmHg",
        },
        "resourceType": "Observation",
    }
    record = Record.from_data(data, sample_config)
    assert record.id == "1"
    assert record.value_quantity == "120"
