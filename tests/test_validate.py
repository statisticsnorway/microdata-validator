import os
import logging
from microdata_validator import validate

logger = logging.getLogger()
logger.setLevel(logging.INFO)
VALID_DATASET_NAME = 'VALID_DATASET'
INVALID_METADATA_DATASET_NAME = 'INVALID_METADATA_DATASET'
INPUT_DIRECTORY = 'tests/resources/input_directory'
WORKING_DIRECTORY = 'tests/resources/working_directory'


def test_validate_valid_dataset():
    data_errors = validate(
        VALID_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY
    )
    actual_files = get_working_directory_files()
    expected_files = [
        f'{VALID_DATASET_NAME}.db',
        f'{VALID_DATASET_NAME}.json',
        f'{VALID_DATASET_NAME}.csv'
    ]
    assert not data_errors
    for file in expected_files:
        assert file in actual_files


def test_validate_invalid_metadata_dataset():
    # improve error handling in reader
    data_errors = validate(
        INVALID_METADATA_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == ["required: 'identifierVariables' is a required property"]


def get_working_directory_files() -> list:
    return [
        file for file in os.listdir(WORKING_DIRECTORY)
        if file != '.gitkeep'
    ]


def teardown_function():
    for file in get_working_directory_files():
        if file != '.gitkeep':
            os.remove(f'{WORKING_DIRECTORY}/{file}')
