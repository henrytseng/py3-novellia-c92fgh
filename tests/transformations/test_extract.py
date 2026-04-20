from app.transformations.extract import extract_field


def test_extract_code():
    data = {
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel",
                }
            ],
            "text": "Blood Pressure",
        }
    }
    assert extract_field(data, "code.coding[0].code", "code")["code"] == "85354-9"


def test_extract_value_quantity():
    data = {"valueQuantity": {"value": 120, "unit": "mmHg"}}
    assert extract_field(data, "valueQuantity.value", "value")["value"] == 120
    assert extract_field(data, "valueQuantity.unit", "unit")["unit"] == "mmHg"
