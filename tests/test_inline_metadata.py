from microdata_validator import inline_metadata
from microdata_validator import utils
from microdata_validator.utils import ParseMetadataError
from pathlib import Path
import pytest
import os


RESOURCES_DIR = "tests/resources/inline_metadata"
OUTPUT_FILE_PATH = "tests/resources/my_inlined_file.json"
KJOENN_FILE_PATH = (
    "tests/resources/input_directory/"
    "SYNT_BEFOLKNING_KJOENN/SYNT_BEFOLKNING_KJOENN.json"
)
KJOENN_DEFAULT_OUTPUT_PATH = (
    "tests/resources/input_directory/"
    "SYNT_BEFOLKNING_KJOENN/SYNT_BEFOLKNING_KJOENN_inlined.json"
)
KJOENN_INLINED_FILE_PATH = f"{RESOURCES_DIR}/SYNT_BEFOLKNING_KJOENN_inlined.json"
SIVSTAND_REFERENCED_FILE_PATH = f"{RESOURCES_DIR}/synt_sivstand_referenced.json"
SIVSTAND_INLINE_FILE_PATH = f"{RESOURCES_DIR}/synt_sivstand_inlined.json"
NONEXISTENT_FILE_PATH = f"{RESOURCES_DIR}/does-not-exist.json"
REF_DIR = "tests/resources/ref_directory"


def test_inline_full_dataset():
    result_file_path = inline_metadata(
        SIVSTAND_REFERENCED_FILE_PATH,
        REF_DIR,
        output_file_path=OUTPUT_FILE_PATH
    )
    actual_inlined = utils.load_json(result_file_path)
    actual_inlined == utils.load_json(
        Path(SIVSTAND_INLINE_FILE_PATH)
    )

def test_inline_full_dataset_no_overwite():
    with pytest.raises(FileExistsError):
        inline_metadata(
            SIVSTAND_REFERENCED_FILE_PATH,
            REF_DIR
        )


def test_inline_full_dataset_default_output_path():
    result_file_path = inline_metadata(
        KJOENN_FILE_PATH,
        REF_DIR
    )
    assert str(result_file_path) == KJOENN_DEFAULT_OUTPUT_PATH  
    actual_inlined = utils.load_json(result_file_path)
    actual_inlined == utils.load_json(
        Path(KJOENN_INLINED_FILE_PATH)
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


def teardown_function():
    try:
        os.remove(OUTPUT_FILE_PATH)
    except:
        pass
    try:
        os.remove(KJOENN_DEFAULT_OUTPUT_PATH)
    except:
        pass 