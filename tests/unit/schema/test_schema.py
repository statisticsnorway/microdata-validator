import pytest
from pathlib import Path

from microdata_validator import schema
from microdata_validator.repository import local_storage
from microdata_validator.exceptions import (
    ParseMetadataError, InvalidDatasetName
)


RESOURCES_DIR = "tests/resources/schema"
SIMPLE_JSON = Path(f"{RESOURCES_DIR}/simple_referenced.json")
SIMPLE_JSON_BAD_REF = Path(f"{RESOURCES_DIR}/simple_bad_reference.json")
SIMPLE_JSON_INLINED = Path(f"{RESOURCES_DIR}/simple_inlined.json")
NONEXISTENT_FILE_PATH = Path(f"{RESOURCES_DIR}/does-not-exist.json")
REF_DIR = Path("tests/resources/ref_directory")


def test_inline_simple():
    actual_inlined = schema.inline_metadata_references(
        SIMPLE_JSON, REF_DIR
    )
    assert actual_inlined == local_storage.load_json(
       SIMPLE_JSON_INLINED
    )


def test_inline_simple_bad_ref():
    with pytest.raises(FileNotFoundError):
        schema.inline_metadata_references(
            SIMPLE_JSON_BAD_REF, REF_DIR
        )


def test_inline_invalid_ref_dir():
    with pytest.raises(ParseMetadataError) as e:
        schema.inline_metadata_references(
            SIMPLE_JSON, None
        )
    assert "No supplied reference directory" in str(e)

    with pytest.raises(ParseMetadataError) as e:
        schema.inline_metadata_references(
            SIMPLE_JSON, SIMPLE_JSON
        )
    assert "Supplied reference directory is invalid" in str(e)


def test_inline_invalid_metadata_file_path():
    with pytest.raises(FileNotFoundError):
        schema.inline_metadata_references(
            NONEXISTENT_FILE_PATH, REF_DIR
        )


def test_validate_dataset_name():
    schema.validate_dataset_name('MITT_DATASET')
    schema.validate_dataset_name('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    schema.validate_dataset_name('123456789')
    schema.validate_dataset_name('1A_2Z3_334_567_GHJ')

    with pytest.raises(InvalidDatasetName):
        schema.validate_dataset_name('ÆØÅ')
    with pytest.raises(InvalidDatasetName):
        schema.validate_dataset_name('MY-!DÅTÆSØT-!?')
    with pytest.raises(InvalidDatasetName):
        schema.validate_dataset_name('MY.DATASET-!?')
