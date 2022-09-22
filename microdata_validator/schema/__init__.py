import json
from pathlib import Path

from jsonschema import validate


def validate_with_schema(metadata_json: dict) -> None:
    json_schema_file = Path(__file__).parent.joinpath(
        "dataset_metadata_schema.json"
    )
    with open(json_schema_file, mode="r", encoding="utf-8") as schema:
        metadata_schema = json.load(schema)
    validate(
        instance=metadata_json,
        schema=metadata_schema
    )
