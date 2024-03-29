import json
import os
import logging

import pytest
from pytest_mock import MockerFixture

from microdata_validator import validate
from microdata_validator.steps import dataset_validator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

VALID_DATASET_NAMES = [
    "SYNT_BEFOLKNING_SIVSTAND",
    "SYNT_PERSON_INNTEKT",
    "SYNT_PERSON_MOR",
    "SYNT_UTDANNING",
]
EMPTY_CSV_DATASET = "EMPTY_CSV_DATASET"
MANY_ERRORS_DATASET = "SYNT_MANY_ERRORS"
VALID_DATASET_REF = "SYNT_BEFOLKNING_KJOENN"
NO_SUCH_DATASET_NAME = "NO_SUCH_DATASET"
WRONG_DELIMITER_DATASET_NAME = "WRONG_DELIMITER_DATASET"
MISSING_IDENTIFIER_DATASET_NAME = "MISSING_IDENTIFIER_DATASET"
INVALID_DATES_DATASET_NAME = "INVALID_DATES_DATASET"
INVALID_DATE_RANGES_DATASET_NAME = "INVALID_DATE_RANGES_DATASET"
INVALID_UNIT_TYPE_DATASET = "INVALID_UNIT_TYPE_DATASET"
INPUT_DIRECTORY = "tests/resources/input_directory"
WORKING_DIRECTORY = "tests/resources/working_directory"
EXPECTED_DIRECTORY = "tests/resources/expected/validate"
REF_DIRECTORY = "tests/resources/ref_directory"


def test_validate_valid_dataset():
    for dataset_name in VALID_DATASET_NAMES:
        data_errors = validate(
            dataset_name,
            working_directory=WORKING_DIRECTORY,
            keep_temporary_files=True,
            input_directory=INPUT_DIRECTORY,
        )
        actual_files = get_working_directory_files()
        expected_files = [
            f"{dataset_name}.db",
            f"{dataset_name}.json",
            f"{dataset_name}.csv",
        ]
        assert not data_errors
        for file in expected_files:
            assert file in actual_files
        with open(
            f"{WORKING_DIRECTORY}/{dataset_name}.json", "r", encoding="utf-8"
        ) as f:
            actual_metadata = json.load(f)
        with open(
            f"{EXPECTED_DIRECTORY}/{dataset_name}.json", "r", encoding="utf-8"
        ) as f:
            expected_metadata = json.load(f)
        assert actual_metadata == expected_metadata


def test_validate_empty_data_file():
    data_errors = validate(
        EMPTY_CSV_DATASET,
        working_directory=WORKING_DIRECTORY,
        keep_temporary_files=True,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        ("Can not read separator from dataset. The .csv file might be empty.",)
    ]


def test_validate_many_errors_threshold():
    data_errors = validate(
        MANY_ERRORS_DATASET,
        working_directory=WORKING_DIRECTORY,
        keep_temporary_files=True,
        input_directory=INPUT_DIRECTORY,
    )
    assert len(data_errors) == 50


def test_validate_valid_dataset_wrong_delimiter():
    data_errors = validate(
        WRONG_DELIMITER_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        keep_temporary_files=True,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == ['Invalid field separator ",". Use ";".']


def test_validate_invalid_unit_type_dataset():
    data_errors = validate(
        INVALID_UNIT_TYPE_DATASET,
        working_directory=WORKING_DIRECTORY,
        keep_temporary_files=True,
        input_directory=INPUT_DIRECTORY,
    )
    assert len(data_errors) == 1
    assert "value is not a valid enumeration member" in data_errors[0]


def test_validate_valid_dataset_delete_temporary_files():
    for valid_dataset_name in VALID_DATASET_NAMES:
        data_errors = validate(
            valid_dataset_name,
            working_directory=WORKING_DIRECTORY,
            input_directory=INPUT_DIRECTORY,
        )
        temp_files = get_working_directory_files()
        assert not data_errors
        assert temp_files == [".gitkeep"]


def test_validate_valid_dataset_delete_generated_dir():
    for valid_dataset_name in VALID_DATASET_NAMES:
        data_errors = validate(
            valid_dataset_name, input_directory=INPUT_DIRECTORY
        )
        temp_files = [
            dir for dir in os.listdir() if os.path.isdir(dir) and dir[0] != "."
        ]
        assert not data_errors
        for file in temp_files:
            assert file in ["tests", "docs", "microdata_validator"]


def test_validate_valid_dataset_ref():
    data_errors = validate(
        VALID_DATASET_REF,
        working_directory=WORKING_DIRECTORY,
        keep_temporary_files=True,
        input_directory=INPUT_DIRECTORY,
        metadata_ref_directory=REF_DIRECTORY,
    )
    actual_files = get_working_directory_files()
    expected_files = [
        f"{VALID_DATASET_REF}.db",
        f"{VALID_DATASET_REF}.json",
        f"{VALID_DATASET_REF}.csv",
    ]
    with open(
        f"{WORKING_DIRECTORY}/{VALID_DATASET_REF}.json", "r", encoding="utf-8"
    ) as f:
        actual_metadata = json.load(f)
    with open(
        f"{EXPECTED_DIRECTORY}/{VALID_DATASET_REF}.json", "r", encoding="utf-8"
    ) as f:
        expected_metadata = json.load(f)
    assert expected_metadata == actual_metadata
    assert not data_errors
    for file in expected_files:
        assert file in actual_files


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
    assert "identifierVariables" in data_errors[0]
    assert "field required" in data_errors[0]


def test_validate_invalid_dates():
    data_errors = validate(
        INVALID_DATES_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        'row 4: STOP date not valid - "1927-13-01"',
        'row 15: STOP date not valid - "1940-02-31"',
    ]


def test_invalid_date_ranges():
    data_errors = validate(
        INVALID_DATE_RANGES_DATASET_NAME,
        working_directory=WORKING_DIRECTORY,
        input_directory=INPUT_DIRECTORY,
    )
    assert data_errors == [
        (
            "row 4: Previous STOP-date greater than STOP-date "
            "- 1926-02-02 > 1926-02-01"
        ),
        (
            "row 13: Previous STOP-date greater than STOP-date"
            " - 1940-01-31 > 1939-02-01"
        ),
    ]


def test_delete_temporary_files_when_exception(mocker: MockerFixture):
    spy = mocker.patch.object(
        dataset_validator,
        "run_validator",
        side_effect=Exception("mocked error"),
    )
    data_errors = None

    with pytest.raises(Exception):
        data_errors = validate(
            "SYNT_BEFOLKNING_SIVSTAND",
            working_directory=WORKING_DIRECTORY,
            input_directory=INPUT_DIRECTORY,
            keep_temporary_files=True,
        )

    spy.assert_called()
    temp_files = get_working_directory_files()
    assert not data_errors
    assert temp_files == [".gitkeep"]


def get_working_directory_files() -> list:
    return os.listdir(WORKING_DIRECTORY)


def teardown_function():
    for file in get_working_directory_files():
        if file != ".gitkeep":
            os.remove(f"{WORKING_DIRECTORY}/{file}")
