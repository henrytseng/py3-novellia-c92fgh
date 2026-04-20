from app.transformations.flatten import flatten_nested


def test_flatten_code():
    data = {
        "code": {
            "coding": [
                {
                    "code": "85354-9",
                }
            ],
            "text": "Blood Pressure",
        }
    }
    assert flatten_nested(data, "code.coding[0]") == {"code": "85354-9"}
