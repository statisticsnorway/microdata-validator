import json
from pathlib import Path

import pytest

from microdata_validator.steps.metadata_inliner import run_inliner
from microdata_validator.adapter import local_storage
from microdata_validator.exceptions import ParseMetadataError


RESOURCES_DIR = "tests/resources/inliner"
SIMPLE_JSON = Path(f"{RESOURCES_DIR}/simple_referenced.json")
SIMPLE_JSON_BAD_REF = Path(f"{RESOURCES_DIR}/simple_bad_reference.json")
SIMPLE_JSON_INLINED = Path(f"{RESOURCES_DIR}/simple_inlined.json")
NONEXISTENT_FILE_PATH = Path(f"{RESOURCES_DIR}/does-not-exist.json")
REF_DIR = Path("tests/resources/ref_directory")


def test_inline_simple():
    actual_inlined = run_inliner(SIMPLE_JSON, REF_DIR)
    assert actual_inlined == local_storage.load_json(SIMPLE_JSON_INLINED)


def test_inline_simple_bad_ref():
    with pytest.raises(FileNotFoundError):
        run_inliner(SIMPLE_JSON_BAD_REF, REF_DIR)


def test_inline_no_ref_dir():
    actual = run_inliner(SIMPLE_JSON, None)
    with open(SIMPLE_JSON, encoding="utf-8") as f:
        expected = json.load(f)
    assert actual == expected

    with pytest.raises(ParseMetadataError) as e:
        run_inliner(SIMPLE_JSON, SIMPLE_JSON)
    assert "Supplied reference directory is invalid" in str(e)


def test_inline_invalid_metadata_file_path():
    with pytest.raises(FileNotFoundError):
        run_inliner(NONEXISTENT_FILE_PATH, REF_DIR)
