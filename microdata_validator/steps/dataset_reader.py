import csv
import datetime
import logging
from pathlib import Path

from microdata_validator import utils
from microdata_validator import temporal_attributes
from microdata_validator.schema import validate_with_schema
from microdata_validator.repository import local_storage


logger = logging.getLogger()


def _insert_data_csv_into_sqlite(sqlite_file_path, dataset_data_file,
                                 field_separator=";") -> None:
    db_conn, cursor = local_storage.create_temp_sqlite_db_file(
        sqlite_file_path
    )
    with open(file=dataset_data_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=field_separator)
        cursor.executemany(
            "INSERT INTO temp_dataset "
            "(row_number, unit_id, value, start, stop, attributes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            reader
        )
    db_conn.commit()
    db_conn.close()
    logger.debug(
        f'Done reading datafile "{dataset_data_file}" '
        'into temp Sqlite database table.'
    )


def _read_and_process_data(data_file_path: Path,
                           enriched_data_file_path: Path,
                           field_separator: str = ";",
                           data_error_limit: int = 100) -> dict:
    data_errors = []  # used for error-reporting
    start_dates = []
    stop_dates = []
    rows_validated = 0

    logger.debug(
        f'Validate datafile "{data_file_path}"'
    )
    data_file_with_row_numbers = open(
        enriched_data_file_path, 'w', encoding='utf-8'
    )
    with open(file=data_file_path, newline='', encoding='utf-8',
              errors="strict") as f:
        csv_sniffer = csv.Sniffer()
        csv_file_separator = csv_sniffer.sniff(f.read(5000)).delimiter
        if csv_file_separator != field_separator:
            error_message = (
                f'Invalid field separator "{csv_file_separator}". Use ";".'
            )
            raise InvalidDataException(error_message, [error_message])

    with open(file=data_file_path, newline='', encoding='utf-8',
              errors="strict") as f:
        reader = csv.reader(f, delimiter=field_separator)
        try:
            for data_row in reader:
                if reader.line_num % 1000000 == 0:
                    logger.debug(f".. now reading row: {reader.line_num}")
                rows_validated += 1
                if len(data_errors) >= data_error_limit:
                    logger.debug(
                        f"Validation stopped - error limit reached, "
                        f"{str(rows_validated)} rows validated"
                    )
                    raise InvalidDataException(
                        'Invalid data found while reading data file',
                        data_errors
                    )

                if not data_row:
                    data_errors.append(
                        f"row {reader.line_num}: "
                        "Empty data row. Expected row with fields "
                        "UNIT_ID, VALUE, (START), (STOP), (ATTRIBUTES))",
                        None
                    )
                elif len(data_row) > 5:
                    data_errors.append(
                        f"row {reader.line_num}: "
                        "Too many elements. Expected row with fields "
                        "UNIT_ID, VALUE, (START), (STOP), (ATTRIBUTES))",
                        None
                    )
                else:
                    unit_id = data_row[0].strip('"')
                    value = data_row[1].strip('"')
                    start = data_row[2].strip('"')
                    stop = data_row[3].strip('"')
                    data_file_with_row_numbers.write(
                        f"{reader.line_num};{unit_id};{value};"
                        f"{start};{stop};\n"
                    )
                    if unit_id is None or str(unit_id).strip(" ") == "":
                        data_errors.append(
                            f"row {reader.line_num}: "
                            f"identifier missing or null - '{unit_id}'"
                        )
                    if value is None or str(value).strip(" ") == "":
                        data_errors.append(
                            f"row {reader.line_num}: "
                            f"measure missing or null - '{value}'"
                        )
                    if start not in (None, ""):
                        try:
                            datetime.datetime(
                                int(start[:4]),
                                int(start[5:7]),
                                int(start[8:10])
                            )
                        except Exception:
                            data_errors.append(
                                f"row {reader.line_num}: "
                                f"START date not valid - '{start}'"
                            )
                    if stop not in (None, ""):
                        try:
                            datetime.datetime(
                                int(stop[:4]), int(stop[5:7]), int(stop[8:10])
                            )
                        except Exception:
                            data_errors.append(
                                f"row {reader.line_num}: "
                                f"STOP date not valid - '{start}'"
                            )
                    # find temporalCoverage from datafile
                    start_dates.append(str(start).strip('"'))
                    stop_dates.append(str(stop).strip('"'))
            data_file_with_row_numbers.close()
        except UnicodeDecodeError as e:
            logger.error(
                f'ERROR (csv.reader error). Data file not UTF-8 encoded. '
                f'File {data_file_path}, near row {reader.line_num}: {e}'
            )
            raise InvalidDataException(
                f'ERROR (csv.reader error). Data file not UTF-8 encoded. '
                f'File {data_file_path}, near row {reader.line_num}: {e}',
                []
            ) from e
        except csv.Error as e:
            logger.error(
                f'ERROR (csv.reader error) in file {data_file_path}, '
                f'near row {reader.line_num}: {e}'
            )
            raise InvalidDataException(
                f'ERROR (csv.reader error) in file {data_file_path}, '
                f'near row {reader.line_num}: {e}',
                []
            ) from e

    if data_errors:
        logger.debug(f"ERROR in file - {data_file_path}")
        logger.debug(f"{str(rows_validated)} rows validated")
        raise InvalidDataException(
            'Invalid data found while reading data file', data_errors
        )
    else:
        logger.debug(f"{str(rows_validated)} rows validated")
        return {
            "start": min(start_dates),
            "latest": max(stop_dates),
            "status_list": list(set(start_dates + stop_dates))
        }


def _metadata_update_temporal_coverage(metadata: dict,
                                       temporal_data: dict) -> None:
    logger.debug(
        'Append temporal coverage (start, stop, status dates) to metadata'
    )
    if metadata["temporalityType"] in ("EVENT", "ACCUMULATED"):
        metadata["dataRevision"]["temporalCoverageStart"] = (
            temporal_data["start"]
        )
        metadata["dataRevision"]["temporalCoverageLatest"] = (
            temporal_data["latest"]
        )
    elif metadata["temporalityType"] == "FIXED":
        metadata["dataRevision"]["temporalCoverageStart"] = (
            "1900-01-01"
        )
        metadata["dataRevision"]["temporalCoverageLatest"] = (
            temporal_data["latest"]
        )
    elif metadata["temporalityType"] == "STATUS":
        temporal_status_dates_list = temporal_data["status_list"]
        temporal_status_dates_list.sort()
        metadata["dataRevision"]["temporalStatusDates"] = (
            temporal_status_dates_list
        )


def run_reader(
    working_directory: Path,
    input_directory: Path,
    metadata_ref_directory: Path,
    dataset_name: str
) -> None:
    metadata_file_path: Path = (
        input_directory / dataset_name / f"{dataset_name}.json"
    )
    data_file_path: Path = (
        input_directory / dataset_name / f"{dataset_name}.csv"
    )

    logger.debug(f'Start reading dataset "{dataset_name}"')
    enriched_data_file_path = working_directory.joinpath(
        f'{dataset_name}.csv'
    )
    temporal_data = _read_and_process_data(
        data_file_path, enriched_data_file_path
    )

    logger.debug(f'Reading metadata from file "{metadata_file_path}"')
    if metadata_ref_directory is None:
        metadata_dict = local_storage.load_json(metadata_file_path)
    else:
        metadata_dict = utils.inline_metadata_references(
            metadata_file_path, metadata_ref_directory
        )

    logger.debug('Validating metadata JSON with JSON schema')
    validate_with_schema(metadata_dict)

    temporality_type = metadata_dict['temporalityType']
    metadata_dict['attributeVariables'] = [
        temporal_attributes.generate_start_time_attribute(temporality_type),
        temporal_attributes.generate_stop_time_attribute(temporality_type)
    ] + metadata_dict.get('attributeVariables', [])
    _metadata_update_temporal_coverage(metadata_dict, temporal_data)

    logger.debug('Writing inlined metadata JSON file to working directory')
    inlined_metadata_file_path = working_directory.joinpath(
        f'{dataset_name}.json'
    )
    local_storage.write_json(inlined_metadata_file_path, metadata_dict)

    sqlite_file_path = working_directory.joinpath(f'{dataset_name}.db')
    _insert_data_csv_into_sqlite(sqlite_file_path, enriched_data_file_path)

    logger.debug(f'OK - reading dataset "{dataset_name}"')


class InvalidDataException(Exception):

    def __init__(self, message: str, data_errors: list):
        self.data_errors = data_errors
        Exception.__init__(self, message)
