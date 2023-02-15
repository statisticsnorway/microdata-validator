import os
import json
import logging
from pathlib import Path

import pytest

from microdata_validator import validate_metadata


logger = logging.getLogger()
logger.setLevel(logging.INFO)

INPUT_DIRECTORY = 'tests/resources/input_directory'
WORKING_DIRECTORY = 'tests/resources/working_directory'
EXPECTED_DIRECTORY = 'tests/resources/expected/validate_metadata'

VALID_METADATA = ['SYNT_BEFOLKNING_SIVSTAND', 'SYNT_PERSON_INNTEKT']
VALID_METADATA_REF = 'SYNT_BEFOLKNING_KJOENN'

NO_SUCH_METADATA = 'NO_SUCH_METADATA'
MISSING_IDENTIFIER_METADATA = 'MISSING_IDENTIFIER_DATASET'
INVALID_SENSITIVITY_METADATA = 'INVALID_SENSITIVITY_DATASET'
EMPTY_CODELIST_METADATA = 'EMPTY_CODELIST_DATASET'
EXTRA_FIELDS_METADATA = 'EXTRA_FIELDS_DATASET'
EXTRA_FIELDS_UNIT_MEASURE_METADATA = 'EXTRA_FIELDS_UNIT_MEASURE_DATASET'
REF_DIRECTORY = 'tests/resources/ref_directory'


def test_validate_valid_metadata():
    for metadata in VALID_METADATA:
        data_errors = validate_metadata(
            metadata,
            input_directory=INPUT_DIRECTORY,
            working_directory=WORKING_DIRECTORY,
            keep_temporary_files=True
        )
        with open(
            Path(WORKING_DIRECTORY) / f'{metadata}.json',
            'r',
            encoding='utf-8'
        ) as f:
            actual_metadata = json.load(f)
        with open(
            Path(EXPECTED_DIRECTORY) / f'{metadata}.json',
            'r',
            encoding='utf-8'
        ) as f:
            expected_metadata = json.load(f)
        assert actual_metadata == expected_metadata
        assert not data_errors


def test_invalid_sensitivity():
    data_errors = validate_metadata(
        INVALID_SENSITIVITY_METADATA, INPUT_DIRECTORY
    )
    assert len(data_errors) == 3
    assert "sensitivityLevel" in str(data_errors[0])
    assert "value is not a valid enumeration member" in str(data_errors[0])


def test_validate_valid_metadata_ref():
    data_errors = validate_metadata(
        VALID_METADATA_REF,
        input_directory=INPUT_DIRECTORY,
        working_directory=WORKING_DIRECTORY,
        metadata_ref_directory=REF_DIRECTORY,
        keep_temporary_files=True
    )
    with open(
        Path(WORKING_DIRECTORY) / f'{VALID_METADATA_REF}.json',
        'r',
        encoding='utf-8'
    ) as f:
        actual_metadata = json.load(f)
    with open(
        Path(EXPECTED_DIRECTORY) / f'{VALID_METADATA_REF}.json',
        'r',
        encoding='utf-8'
    ) as f:
        expected_metadata = json.load(f)
    assert actual_metadata == expected_metadata
    assert not data_errors


def test_validate_invalid_metadata():
    data_errors = validate_metadata(
        MISSING_IDENTIFIER_METADATA,
        input_directory=INPUT_DIRECTORY
    )
    assert 'identifierVariables' in data_errors[0]['loc']
    assert data_errors[0]['msg'] == 'field required'


def test_validate_empty_codelist():
    data_errors = validate_metadata(
        EMPTY_CODELIST_METADATA,
        input_directory=INPUT_DIRECTORY
    )
    assert 'codeList' in data_errors[0]['loc']
    assert 'ensure this value has at least 1 items' in data_errors[0]['msg']


def test_invalidate_extra_fields():
    data_errors = validate_metadata(
        EXTRA_FIELDS_METADATA,
        input_directory=INPUT_DIRECTORY
    )
    assert len(data_errors) == 4
    for data_error in data_errors:
        assert data_error['msg'] == 'extra fields not permitted'


def test_invalidate_extra_fields_unit_type_measure():
    data_errors = validate_metadata(
        EXTRA_FIELDS_UNIT_MEASURE_METADATA,
        input_directory=INPUT_DIRECTORY
    )
    assert len(data_errors) == 1
    assert data_errors[0]['msg'] == (
        'Can not set a dataType in a measure variable together with a unitType'
    )


def test_validate_metadata_does_not_exist():
    with pytest.raises(FileNotFoundError):
        validate_metadata(NO_SUCH_METADATA, INPUT_DIRECTORY)


def get_working_directory_files() -> list:
    return os.listdir(WORKING_DIRECTORY)


def teardown_function():
    for file in get_working_directory_files():
        if file != '.gitkeep':
            os.remove(f'{WORKING_DIRECTORY}/{file}')
