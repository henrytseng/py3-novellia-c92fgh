import pytest
import json

with open("tmp/missing_data.jsonl", "r") as f:
    missing_data = [json.loads(line) for line in f if line.strip()]

def test_dummy():
    assert len(missing_data) == 72
