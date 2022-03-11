from microdata_validator import utils
from microdata_validator.utils import ParseMetadataError
from pathlib import Path
import pytest

RESOURCES_DIR = "tests/resources/inline_metadata"
SIVSTAND_REFERENCED_FILE_PATH = Path(f"{RESOURCES_DIR}/sivstand_referenced.json")
SIVSTAND_INLINE_FILE_PATH = Path(f"{RESOURCES_DIR}/sivstand_inline.json")
NONEXISTENT_FILE_PATH = Path(f"{RESOURCES_DIR}/does-not-exist.json")
METADATA_FILE_PATH = Path(f"{RESOURCES_DIR}/simple_referenced.json")
EXPECTED_METADATA_FILE_PATH = Path(f"{RESOURCES_DIR}/simple_inlined.json")
REF_DIR = Path("tests/resources/ref_directory")


def test_inline_simple():
    actual_inlined = utils.inline_metadata_references(
        METADATA_FILE_PATH, REF_DIR
    )
    assert actual_inlined == utils.load_json(
       EXPECTED_METADATA_FILE_PATH
    )


def test_inline_full_dataset():
    actual_inlined = utils.inline_metadata_references(
        SIVSTAND_REFERENCED_FILE_PATH, REF_DIR
    )
    actual_inlined == utils.load_json(
        SIVSTAND_INLINE_FILE_PATH
    )


def test_inline_invalid_metadata_file_path():
    with pytest.raises(FileNotFoundError):
        utils.inline_metadata_references(
            NONEXISTENT_FILE_PATH, REF_DIR
        )

def test_inline_invalid_ref_dir():
    with pytest.raises(ParseMetadataError) as e:
        utils.inline_metadata_references(
            SIVSTAND_REFERENCED_FILE_PATH, None
        )
    assert "No supplied reference directory" in str(e)

    with pytest.raises(ParseMetadataError) as e:
        utils.inline_metadata_references(
            SIVSTAND_REFERENCED_FILE_PATH, SIVSTAND_REFERENCED_FILE_PATH
        )
    assert "Supplied reference directory is invalid" in str(e)


def test_inline_invalid_ref():
    pass