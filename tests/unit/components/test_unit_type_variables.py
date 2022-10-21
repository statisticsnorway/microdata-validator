import json
from pathlib import Path
from jsonschema import validate

from microdata_validator.components.unit_type_variables import (
    UNIT_TYPE_VARIABLES
)

SCHEMA_PATH = Path('tests/resources/components/unit_type_variable_schema.json')
with open(SCHEMA_PATH, mode="r", encoding="utf-8") as schema:
    metadata_schema = json.load(schema)


def test_unit_type_variables_format():
    for _, variable in UNIT_TYPE_VARIABLES.items():
        validate(
            instance=variable,
            schema=metadata_schema
        )
