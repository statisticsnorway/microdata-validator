import datetime
from typing import Union
import logging
from pathlib import Path
from microdata_validator import file_utils

logger = logging.getLogger()


def __get_data_type(metadata: dict) -> str:
    return metadata["measureVariables"][0]["dataType"]


def __get_code_list_with_missing_values(metadata: dict) -> Union[list, None]:
    """get codeList if exists in enumerated-valueDomain"""
    meta_value_domain_codes = None
    value_domain = metadata["measureVariables"][0]["valueDomain"]
    if "codeList" in value_domain:
        meta_value_domain_codes = [
            item["code"] for item in value_domain["codeList"]["codeItems"]
        ]
    if "sentinelAndMissingValues" in value_domain:
        meta_value_domain_codes += [
            missing_item["code"] for missing_item
            in value_domain["sentinelAndMissingValues"]
        ]
    return meta_value_domain_codes


def __validate_data(sqlite_db_file_path: str, metadata: dict) -> int:
    """Read and validate sorted data rows from the temporary Sqlite 
       database file (sorted by unit_id, start, stop)
    """
    db_conn, db_cursor = file_utils.read_temp_sqlite_db_data_sorted(
        sqlite_db_file_path
    )
    temporality_type = metadata["temporalityType"]
    data_type = __get_data_type(metadata)
    code_list_with_missing_values = __get_code_list_with_missing_values(metadata)
    previous_data_row = (None, None, None, None, None)
    data_errors = []

    # data-rows in cursor sorted by unit_id, start, stop
    for data_row in db_cursor:
        row_errors = [
            __is_data_row_consistent(
                temporality_type, data_row, previous_data_row
            ),
            __is_data_row_consistent_with_metadata(
                data_type, code_list_with_missing_values, data_row
            )
        ]
        data_errors += row_errors
        previous_data_row = data_row
    db_conn.close()
    return [error for error in data_errors if error is not None]


def __is_data_row_consistent(temporality_type: str, data_row: tuple,
                             previous_data_row: tuple) -> Union[tuple, None]:
    """Validate consistency and event-history (unit_id * start * stop)
       and check for row duplicates.
    """
    row_number = previous_data_row[0]
    unit_id = data_row[1]
    # value = data_row[2]
    start = data_row[3]
    stop = data_row[4]
    # attributes = data_row[5]

    prev_row_number = previous_data_row[0]
    prev_unit_id = previous_data_row[1]
    # prev_value = previous_data_row[2]
    prev_start = previous_data_row[3]
    prev_stop = previous_data_row[4]
    # prev_attributes = previous_data_row[5]

    if data_row[1:] == previous_data_row[1:]:
        return (
            row_number,
            "Data row duplicate (2 or more equal rows in datafile)"
        )
    if (unit_id == prev_unit_id) and (start == prev_start):
        return (
            row_number,
            "2 or more rows with same UNIT_ID and START-date"
        )
    # Valid temporalityTypes: "FIXED", "STATUS", "ACCUMULATED", "EVENT"
    if temporality_type in ("STATUS", "ACCUMULATED", "EVENT"):
        if start is None or str(start).strip() == "":
            return (
                row_number,
                f"Expected START-date when temporalityType is {temporality_type}"
            )
        if (stop not in (None, "")) and (start > stop):
            return (
                row_number,
                f"START-date greater than STOP-date: {start} --> {stop}"
            )
        if temporality_type in ("STATUS", "ACCUMULATED"):
            # if str(stop).strip in(None, ""):
            if stop is None or str(stop).strip() == "":
                return (
                    row_number,
                    f"Expected STOP-date when temporalityType is {temporality_type}"
                )
        if temporality_type == "STATUS":
            if not start == stop:
                return (
                    row_number,
                    f"START-date should equal STOP-date when DataSet.temporalityType is {temporality_type}"
                )
        if temporality_type == "EVENT":
            if unit_id == prev_unit_id and not prev_stop:
                return (
                    row_number,
                    f"previous event not ended (missing STOP-date in line/row {prev_row_number})"
                )
            if (unit_id == prev_unit_id) and (start < prev_stop):
                return (
                    row_number,
                    (
                        "Inconsistency - previous STOP-date is greater "
                        "than START-date"
                    )
                )
    elif temporality_type == "FIXED":
        if unit_id == prev_unit_id:
            return (
                row_number,
                (
                    "Inconsistency - 2 or more rows with same UNIT_ID "
                    "(data row duplicate) not legal when "
                    f"DataSet.temporalityType is {temporality_type}"
                )
            )
        if stop is None or str(stop).strip() == "":
            return (
                row_number,
                f"Expected STOP-date when temporalityType is {temporality_type}"
            )
        if not (start is None or str(start).strip() == ""):
            print(start)
            return (
                row_number,
                f"There should be no START-date when temporalityType is {temporality_type}"
            )
    return None


def __is_data_row_consistent_with_metadata(data_type:str,
                                           code_list_with_missing_values: list,
                                           data_row: tuple) -> Union[tuple, None]:
    row_number = data_row[0]
    # unit_id = data_row[1]
    value = data_row[2]
    # start = data_row[3]
    # stop = data_row[4]
    # attributes = data_row[5]

    if code_list_with_missing_values:
        # Enumerated value-domain for variable - check if value exsists in CodeList
        value_string = str(value).strip('"')
        if value_string not in code_list_with_missing_values:
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
                "Inconsistency - value not of type LONG"
            )
    elif data_type == "DOUBLE":
        try:
            float(str(value).strip('"'))
        except Exception:
            return (
                row_number,
                "Inconsistency - value not of type DOUBLE"
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
                "Inconsistency - value not of type DATE (YYYY-MM-DD)"
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
