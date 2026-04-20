import copy


def extract_field(data: dict, field_descriptor: str, as_field: str) -> dict:
    """
    Extracts a field value from a dictionary or nested structure.

    Example:
    >>> data = {
    ...     "code": {
    ...         "coding": [
    ...             {
    ...                 "system": "http://loinc.org",
    ...                 "code": "85354-9",
    ...                 "display": "Blood pressure panel"
    ...             }
    ...         ],
    ...         "text": "Blood Pressure"
    ...     }
    ... }
    >>> extract_field(data, "code.coding[0].code", "code")
    {'code': '85354-9'}
    """
    current_value = data
    path_elements = field_descriptor.split(".")

    for element in path_elements:
        # Not able to iterate
        if not isinstance(current_value, list | dict):
            return copy.deepcopy(data)

        if "[" in element and "]" in element:
            key, index = element.split("[")
            index = int(index.strip("]"))
        else:
            key = element
            index = None

        # Path not found
        if key not in current_value:
            return copy.deepcopy(data)

        # Handle iterable
        if index is not None:
            current_value = current_value[key][index]
        else:
            current_value = current_value[key]

    return copy.deepcopy(data) | {as_field: current_value}
