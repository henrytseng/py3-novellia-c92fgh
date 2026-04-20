import copy


def flatten_nested(data: dict, field_descriptor: str, **kwargs) -> dict:
    """
    Flattens a nested value using a field path.

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
    >>> flatten_nested(data, "code.coding[0]")
    {'code': '85354-9'}
    """
    current_value = data
    path_elements = field_descriptor.split(".")

    print(data, field_descriptor)

    for element in path_elements:
        print(element)

        # Not able to iterate
        if not isinstance(current_value, list | dict):
            return copy.deepcopy(data)

        # Handle iterable
        if "[" in element and "]" in element:
            element, index = element.split("[")
            index = int(index.strip("]"))
            current_value = current_value[element][index]
        else:
            current_value = current_value[element]

    return copy.deepcopy(data) | copy.deepcopy(current_value)
