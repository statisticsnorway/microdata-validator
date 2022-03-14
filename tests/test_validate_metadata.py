import logging
from microdata_validator import validate_metadata
import pytest

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INPUT_DIR = 'tests/resources/input_directory'
VALID_METADATA_FILE_PATHS = [
    f'{INPUT_DIR}/SYNT_BEFOLKNING_SIVSTAND/SYNT_BEFOLKNING_SIVSTAND.json',
    f'{INPUT_DIR}/SYNT_PERSON_INNTEKT/SYNT_PERSON_INNTEKT.json'
]
VALID_METADATA_REF_PATH = f'{INPUT_DIR}/SYNT_BEFOLKNING_KJOENN/SYNT_BEFOLKNING_KJOENN.json'
NO_SUCH_METADATA_FILE = 'NO/SUCH/FILE'
MISSING_IDENTIFIER_METADATA_FILE_PATH = (
    f'{INPUT_DIR}/MISSING_IDENTIFIER_DATASET/MISSING_IDENTIFIER_DATASET.json'
)
REF_DIRECTORY = 'tests/resources/ref_directory'

def test_validate_valid_metadata():
    for metadata_file_path in VALID_METADATA_FILE_PATHS:
        data_errors = validate_metadata(
            metadata_file_path
        )
        assert not data_errors


def test_validate_valid_metadata_ref():
    data_errors = validate_metadata(
        VALID_METADATA_REF_PATH,
        metadata_ref_directory=REF_DIRECTORY
    )
    assert not data_errors


def test_validate_invalid_metadata():
        data_errors = validate_metadata(
            MISSING_IDENTIFIER_METADATA_FILE_PATH
        )
        assert data_errors == [
            "required: 'identifierVariables' is a required property"
        ]


def test_validate_metadata_does_not_exist():
    with pytest.raises(FileNotFoundError) as e:
        validate_metadata(
            NO_SUCH_METADATA_FILE
        )
