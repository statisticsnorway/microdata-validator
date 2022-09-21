from microdata_validator import utils
from microdata_validator.utils import ParseMetadataError
from pathlib import Path
import pytest

RESOURCES_DIR = "tests/resources/inline_metadata"
SIMPLE_JSON = Path(f"{RESOURCES_DIR}/simple_referenced.json")
SIMPLE_JSON_BAD_REF = Path(f"{RESOURCES_DIR}/simple_bad_reference.json")
SIMPLE_JSON_INLINED = Path(f"{RESOURCES_DIR}/simple_inlined.json")
NONEXISTENT_FILE_PATH = Path(f"{RESOURCES_DIR}/does-not-exist.json")
REF_DIR = Path("tests/resources/ref_directory")


def test_inline_simple():
    actual_inlined = utils.inline_metadata_references(
        SIMPLE_JSON, REF_DIR
    )
    assert actual_inlined == utils.load_json(
       SIMPLE_JSON_INLINED
    )


def test_inline_simple_bad_ref():
    with pytest.raises(FileNotFoundError):
        utils.inline_metadata_references(
            SIMPLE_JSON_BAD_REF, REF_DIR
        )


def test_inline_invalid_ref_dir():
    with pytest.raises(ParseMetadataError) as e:
        utils.inline_metadata_references(
            SIMPLE_JSON, None
        )
    assert "No supplied reference directory" in str(e)

    with pytest.raises(ParseMetadataError) as e:
        utils.inline_metadata_references(
            SIMPLE_JSON, SIMPLE_JSON
        )
    assert "Supplied reference directory is invalid" in str(e)


def test_inline_invalid_metadata_file_path():
    with pytest.raises(FileNotFoundError):
        utils.inline_metadata_references(
            NONEXISTENT_FILE_PATH, REF_DIR
        )
