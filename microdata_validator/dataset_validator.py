import datetime
from typing import Union
import logging
from pathlib import Path
from microdata_validator import file_utils

logger = logging.getLogger()


def __get_metadata_measure_variable(metadata: dict):
    return next(
        variable for variable in metadata["variables"]
        if variable.get("variableRole") == "MEASURE"
    )


def __get_metadata_measure_code_list(metadata: dict) -> Union[list, None]:
    """get codeList if exists in enumerated-valueDomain"""
    meta_value_domain_codes = None
    metadata_measure_variable = __get_metadata_measure_variable(
        metadata
    )
    value_domain = metadata_measure_variable["valueDomain"]
    if "codeList" in value_domain:
        meta_value_domain_codes = [
            item["code"] for item in value_domain["codeList"]["codeItems"]
        ]
    return meta_value_domain_codes


def __get_metadata_measure_sentinel_missing_values(metadata: dict) -> Union[list, None]:
    meta_missing_values = None
    metadata_measure_variable = __get_metadata_measure_variable(
        metadata
    )
    value_domain = metadata_measure_variable["valueDomain"]
    if "sentinelAndMissingValues" in value_domain:
        meta_missing_values = [
            missing_item["code"] for missing_item
            in value_domain["sentinelAndMissingValues"]
        ]
    return meta_missing_values


def __validate_data(sqlite_db_file_path: str, metadata: dict) -> int:
    """Read and validate sorted data rows from the temporary Sqlite 
       database file (sorted by unit_id, start, stop)
    """
    db_conn, db_cursor = file_utils.read_temp_sqlite_db_data_sorted(
        sqlite_db_file_path
    )
    row_number = 0
    temporality_type = metadata["temporalityType"]
    previous_data_row = (None, None, None, None, None)
    data_errors = []
    # data-rows in cursor sorted by unit_id, start, stop
    for data_row in db_cursor:
        row_number += 1
        if row_number % 1000000 == 0:
            logger.info(f".. now validating row: {row_number}")
        row_errors = [
            __is_data_row_consistent(
                temporality_type, data_row,
                previous_data_row, row_number
            ),
            __is_data_row_consistent_with_metadata(
                metadata, data_row, row_number
            )
        ]
        data_errors += row_errors
        previous_data_row = data_row
    db_conn.close()
    return [error for error in data_errors if error is not None]


def __is_data_row_consistent(temporality_type: str, data_row: tuple,
                             previous_data_row: tuple,
                             row_number: int) -> Union[tuple, None]:
    """Validate consistency and event-history (unit_id * start * stop)
       and check for row duplicates.
    """
    unit_id = data_row[0]
    # value = data_row[1]
    start = data_row[2]
    stop = data_row[3]
    # attributes = data_row[4]
    prev_unit_id = previous_data_row[0]
    # prev_value = previous_data_row[1]
    prev_start = previous_data_row[2]
    prev_stop = previous_data_row[3]
    # prev_attributes = previous_data_row[4]

    if data_row == previous_data_row:
        return (
            row_number,
            (
                "Inconsistency - Data row duplicate "
                "(2 or more equal rows in datafile)"
            ),
            None
        )
    if (unit_id == prev_unit_id) and (start == prev_start):
        return (
            row_number,
            "Inconsistency - 2 or more rows with same UNIT_ID and START-date",
            None
        )
    # Valid temporalityTypes: "FIXED", "STATUS", "ACCUMULATED", "EVENT"
    if temporality_type in ("STATUS", "ACCUMULATED", "EVENT"):
        if start is None or str(start).strip(" ") == "":
            return (
                row_number,
                (
                    "Inconsistency - START-date is missing. "
                    "Expected START-date when DataSet.temporalityType"
                    f"is {temporality_type}"
                ),
                None
            )
        if (stop not in (None, "")) and (start > stop):
            return (
                row_number,
                "Inconsistency - START-date greater than STOP-date.",
                f"{start} --> {stop}"
            )
        if temporality_type in ("STATUS", "ACCUMULATED"):
            # if str(stop).strip in(None, ""):
            if stop is None or str(stop).strip(" ") == "":
                return (
                    row_number,
                    (
                        "Inconsistency - STOP-date is missing. "
                        "Expected STOP-date when DataSet.temporalityType "
                        f"is {temporality_type}"
                    ),
                    None
                )
        if temporality_type == "STATUS":
            if not start == stop:
                return (
                    row_number,
                    (
                        "Inconsistency - expected same (equal) date for "
                        "START-date and STOP-date when DataSet.temporalityType"
                        f" is {temporality_type}"
                    ),
                    None
                )
        if temporality_type == "EVENT":
            if unit_id == prev_unit_id and not prev_stop:
                return (
                    row_number,
                    (
                        "Inconsistency - previous row not ended "
                        f"(missing STOP-date in line/row {row_number-1})"
                    ),
                    None
                )
            if (unit_id == prev_unit_id) and (start < prev_stop):
                return (
                    row_number,
                    (
                        "Inconsistency - previous STOP-date is greater "
                        "than START-date"
                    ),
                    None
                )
    elif temporality_type == "FIXED":
        if unit_id == prev_unit_id:
            return (
                row_number,
                (
                    "Inconsistency - 2 or more rows with same UNIT_ID "
                    "(data row duplicate) not legal when "
                    f"DataSet.temporalityType is {temporality_type}"
                ),
                None
            )
    return None


def __is_data_row_consistent_with_metadata(metadata: dict, data_row: tuple,
                                           row_number: int) -> Union[tuple, None]:
    data_type = __get_metadata_measure_variable(metadata)["dataType"]
    code_list = __get_metadata_measure_code_list(metadata)
    sentinel_missing_values = __get_metadata_measure_sentinel_missing_values(
        metadata
    )
    # unit_id = data_row[0]
    value = data_row[1]
    # start = data_row[2]
    # stop = data_row[3]
    # attributes = data_row[4]

    if code_list:
        # Enumerated value-domain for variable - check if value exsists in CodeList
        value_string = str(value).strip('"')
        if value_string not in code_list + sentinel_missing_values:
            return (
                row_number,
                (
                    "Inconsistency - value (code) not in metadata "
                    "ValueDomain/CodeList or SentinelAndMissingValues-list",
                ),
                value
            )
    # else:
    # Described value-domian for variable (e.g. amount, weight, length, ..)

    # Valid datatypes: "STRING", "LONG", "DOUBLE", "DATE"
    if data_type == "LONG":
        try:
            int(str(value).strip('"'))
        except Exception:
            return (
                row_number,
                "Inconsistency - value not of type LONG",
                None
            )
    elif data_type == "DOUBLE":
        try:
            float(str(value).strip('"'))
        except Exception:
            return (
                row_number,
                "Inconsistency - value not of type DOUBLE",
                None
            )
    elif data_type == "DATE":
        try:
            # datetime.datetime.strptime(value, "%Y-%m-%d")
            datetime.datetime(
                int(value[:4]), int(value[5:7]), int(value[8:10])
            )
        except Exception:
            return (
                row_number,
                "Inconsistency - value not of type DATE (YYYY-MM-DD)",
                None
            )
    return None


def run_validator(working_directory: Path, dataset_name: str) -> list:
    metadata_file_path: Path = working_directory.joinpath(f'{dataset_name}.json')
    sqlite_file_path: Path = working_directory.joinpath(f"{dataset_name}.db")
    logger.info(
        f'Dataset "{dataset_name}" - validate consistency between '
        f'data and metadata, event-history (unit_id '
        f'* start * stop) and check for row duplicates'
    )
    metadata = file_utils.load_json(metadata_file_path)
    data_errors = __validate_data(sqlite_file_path, metadata)
    if len(data_errors) > 0:
        logger.error(f'ERROR - data consistency error(s):')
        for error in data_errors:
           logger.error(f'{error[1]}')
        return data_errors
    else:
        logger.info(
            f'OK - consistency validation for dataset "{dataset_name}"'
        )
        return []
