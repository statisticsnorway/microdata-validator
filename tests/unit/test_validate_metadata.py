import logging

import pytest

from microdata_validator import validate_metadata


logger = logging.getLogger()
logger.setLevel(logging.INFO)

INPUT_DIR = 'tests/resources/input_directory'
VALID_METADATA = ['SYNT_BEFOLKNING_SIVSTAND', 'SYNT_PERSON_INNTEKT']
VALID_METADATA_REF = 'SYNT_BEFOLKNING_KJOENN'
NO_SUCH_METADATA = 'NO_SUCH_METADATA'
MISSING_IDENTIFIER_METADATA = 'MISSING_IDENTIFIER_DATASET'
INVALID_SENSITIVITY_METADATA = 'INVALID_SENSITIVITY_DATASET'
EMPTY_CODELIST_METADATA = 'EMPTY_CODELIST_DATASET'
REF_DIRECTORY = 'tests/resources/ref_directory'


def test_validate_valid_metadata():
    for metadata in VALID_METADATA:
        data_errors = validate_metadata(metadata, INPUT_DIR)
        assert not data_errors


def test_invalid_sensitivity():
    data_errors = validate_metadata(INVALID_SENSITIVITY_METADATA, INPUT_DIR)
    assert len(data_errors) == 1
    assert "'UNKNOWN' is not one of" in data_errors[0]


def test_validate_valid_metadata_ref():
    data_errors = validate_metadata(
        VALID_METADATA_REF,
        INPUT_DIR,
        metadata_ref_directory=REF_DIRECTORY
    )
    assert not data_errors


def test_validate_invalid_metadata():
    data_errors = validate_metadata(MISSING_IDENTIFIER_METADATA, INPUT_DIR)
    assert data_errors == [
        "required: 'identifierVariables' is a required property"
    ]


def test_validate_empty_codelist():
    data_errors = validate_metadata(EMPTY_CODELIST_METADATA, INPUT_DIR)
    assert data_errors == [
        (
            'properties.measureVariables.items.properties'
            '.valueDomain.properties.codeList.minItems: '
            '[] is too short'
        )
    ]


def test_validate_metadata_does_not_exist():
    with pytest.raises(FileNotFoundError):
        validate_metadata(NO_SUCH_METADATA, INPUT_DIR)
