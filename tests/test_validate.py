import os
import logging
from microdata_validator import validate
import pytest

logger = logging.getLogger()
logger.setLevel(logging.INFO)

VALID_DATASET_NAMES = [
    'SYNT_BEFOLKNING_KJOENN', 'SYNT_BEFOLKNING_SIVSTAND', 'SYNT_PERSON_INNTEKT'
]
NO_SUCH_DATASET_NAME = 'NO_SUCH_DATASET'
MISSING_IDENTIFIER_DATASET_NAME = 'MISSING_IDENTIFIER_DATASET'
INVALID_DATES_DATASET_NAME = 'INVALID_DATES_DATASET'
INVALID_DATE_RANGES_DATASET_NAME = 'INVALID_DATE_RANGES_DATASET'
INPUT_DIRECTORY = 'tests/resources/input_directory'
WORKING_DIRECTORY = 'tests/resources/working_directory'


def test_validate_valid_dataset():
    for valid_dataset_name in VALID_DATASET_NAMES:
        data_errors = validate(
            valid_dataset_name,
            working_directory=WORKING_DIRECTORY,
            input_directory=INPUT_DIRECTORY
        )
        actual_files = get_working_directory_files()
        expected_files = [
            f'{valid_dataset_name}.db',
            f'{valid_dataset_name}.json',
            f'{valid_dataset_name}.csv'
        ]
        assert not data_errors
        for file in expected_files:
            assert file in actual_files


def test_validate_valid_dataset_delete_working_files():
    for valid_dataset_name in VALID_DATASET_NAMES:
        data_errors = validate(
            valid_dataset_name,
            working_directory=WORKING_DIRECTORY,
            input_directory=INPUT_DIRECTORY,
            delete_working_directory=True
        )
        actual_files = get_working_directory_files()
        assert not data_errors
        assert not actual_files


def test_dataset_does_not_exist():
    with pytest.raises(FileNotFoundError):
        validate(
            NO_SUCH_DATASET_NAME,
            working_directory=WORKING_DIRECTORY,
            input_directory=INPUT_DIRECTORY,
        )


def test_validate_missing_identifier():
    data_errors = validate(
        MISSING_IDENTIFIER_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        "required: 'identifierVariables' is a required property"
    ]


def test_validate_invalid_dates():
    data_errors = validate(
        INVALID_DATES_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        (4, 'STOP-date not valid', '1927-13-01'),
        (15, 'STOP-date not valid', '1940-02-31')
    ]


def test_invalid_date_ranges():
    data_errors = validate(
        INVALID_DATE_RANGES_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        (4, 'Inconsistency - previous STOP-date is greater than START-date'),
        (13, 'Inconsistency - previous STOP-date is greater than START-date'),
    ]


def get_working_directory_files() -> list:
    return [
        file for file in os.listdir(WORKING_DIRECTORY)
        if file != '.gitkeep'
    ]


def teardown_function():
    for file in get_working_directory_files():
        if file != '.gitkeep':
            os.remove(f'{WORKING_DIRECTORY}/{file}')
