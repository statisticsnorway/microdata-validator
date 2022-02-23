import csv
import datetime
import logging
from shutil import copyfile
from pathlib import Path
from microdata_validator import file_utils

logger = logging.getLogger()


def __inline_metadata_references(metadata_file_path: Path) -> dict:
    # This function is currently not supported in MVP of this library.
    # Will be implemented ASAP.
    logger.info(f'Reading metadata from file "{metadata_file_path}"')

    # metadata_ref_directory = Path(__file__).parent.joinpath("metadata_ref")
    metadata: dict = file_utils.load_json(metadata_file_path)
    return metadata


def __insert_data_csv_into_sqlite(sqlite_file_path, dataset_data_file,
                                  field_separator=";") -> None:
    db_conn, cursor = file_utils.create_temp_sqlite_db_file(
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
    logger.info(
        f'Done reading datafile "{dataset_data_file}" '
        'into temp Sqlite database table.'
    )


def __read_and_process_data(data_file_path: Path,
                            enriched_data_file_path: Path,
                            field_separator: str = ";",
                            data_error_limit: int = 100) -> dict:
    data_errors = []  # used for error-reporting
    start_dates = []
    stop_dates = []
    rows_validated = 0

    logger.info(
        f'Validate datafile "{data_file_path}"'
    )
    data_file_with_row_numbers = open(enriched_data_file_path, 'w')
    with open(file=data_file_path, newline='', encoding='utf-8', errors="strict") as f:
        reader = csv.reader(f, delimiter=field_separator)
        try:
            for data_row in reader:
                if reader.line_num % 1000000 == 0:
                    logger.info(".. now reading row: " + str(reader.line_num))
                rows_validated += 1
                if len(data_errors) >= data_error_limit:
                    logger.error(f"ERROR in file - {data_file_path}")
                    logger.error(
                        f"Validation stopped - error limit reached, "
                        f"{str(rows_validated)} rows validated"
                    )
                    raise InvalidDataException(
                        f'Invalid data found while reading data file', data_errors
                    )

                if not data_row:
                    data_errors.append((
                        reader.line_num,
                        "Empty data row/line (Null/missing). "
                        "Expected row with fields "
                        "UNIT_ID, VALUE, (START), (STOP), (ATTRIBUTES))",
                        None
                    ))
                elif len(data_row) > 5:
                    data_errors.append((
                        reader.line_num,
                        "Too many elements in row/line. "
                        "Expected row with fields "
                        "UNIT_ID, VALUE, (START), (STOP), (ATTRIBUTES))",
                        None
                    ))
                else:
                    unit_id = data_row[0].strip('"')
                    value = data_row[1].strip('"')
                    start = data_row[2].strip('"')
                    stop = data_row[3].strip('"')
                    # TODO: attributes = data_row[4]
                    data_file_with_row_numbers.write(
                        f"{reader.line_num};{unit_id};{value};{start};{stop};\n"
                    )
                    if unit_id is None or str(unit_id).strip(" ") == "":
                        data_errors.append((
                            reader.line_num,
                            "UNIT_ID (identifier) missing or null",
                            unit_id
                        ))
                    if value is None or str(value).strip(" ") == "":
                        data_errors.append((
                            reader.line_num,
                            "VALUE (measure) missing or null",
                            value
                        ))
                    if start not in (None, ""):
                        try:
                            datetime.datetime(
                                int(start[:4]), int(start[5:7]), int(start[8:10])
                            )
                        except Exception:
                            data_errors.append((
                                reader.line_num,
                                "START-date not valid",
                                start
                            ))
                    if stop not in (None, ""):
                        try:
                            datetime.datetime(
                                int(stop[:4]), int(stop[5:7]), int(stop[8:10])
                            )
                        except Exception:
                            data_errors.append((
                                reader.line_num,
                                "STOP-date not valid",
                                stop
                            ))
                    # TODO: validate "attributes"?

                    # find temporalCoverage from datafile
                    start_dates.append(str(start).strip('"'))
                    stop_dates.append(str(stop).strip('"'))
            data_file_with_row_numbers.close()
        except UnicodeDecodeError as ue:
            # See https://stackoverflow.com/questions/3269293/how-to-write-a-check-in-python-to-see-if-file-is-valid-utf-8
            logger.error(
                f'ERROR (csv.reader error). Data file not UTF-8 encoded. '
                f'File {data_file_path}, near line {reader.line_num}: {ue}'
            )
            raise InvalidDataException(
                f'ERROR (csv.reader error). Data file not UTF-8 encoded. '
                f'File {data_file_path}, near line {reader.line_num}: {ue}'
            )
        except csv.Error as e:
            logger.error(
                f'ERROR (csv.reader error) in file {data_file_path}, '
                f'near line {reader.line_num}: {e}'
            )
            raise InvalidDataException(
                f'ERROR (csv.reader error) in file {data_file_path}, '
                f'near line {reader.line_num}: {e}'
            )

    if data_errors:
        logger.error(f"ERROR in file - {data_file_path}")
        logger.info(f"{str(rows_validated)} rows validated")
        raise InvalidDataException(
            f'Invalid data found while reading data file', data_errors
        )
    else:
        logger.info(f"{str(rows_validated)} rows validated")
        return {
            "start": min(start_dates),
            "latest": max(stop_dates),
            "status_list": list(set(start_dates + stop_dates))
        }


def __metadata_update_temporal_coverage(metadata: dict,
                                        temporal_data: dict) -> None:
    logger.info(
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
        temporalStatusDatesList = temporal_data["status_list"]
        temporalStatusDatesList.sort()
        metadata["dataRevision"]["temporalStatusDates"] = (
            temporalStatusDatesList
        )


def run_reader(working_directory: Path, input_directory: Path,
               dataset_name: str) -> None:
    metadata_file_path: Path = (
        input_directory / dataset_name / f"{dataset_name}.json"
    )
    data_file_path: Path = (
        input_directory / dataset_name / f"{dataset_name}.csv"
    )

    logger.info(f'Start reading dataset "{dataset_name}"')
    enriched_data_file_path = working_directory.joinpath(
        f'{dataset_name}.csv'
    )
    temporal_data = __read_and_process_data(
        data_file_path, enriched_data_file_path
    )

    metadata_dict = __inline_metadata_references(metadata_file_path)
    __metadata_update_temporal_coverage(metadata_dict, temporal_data)

    logger.info('Writing inlined metadata JSON file to working directory')
    inlined_metadata_file_path = working_directory.joinpath(
        f'{dataset_name}.json'
    )
    file_utils.write_json(inlined_metadata_file_path, metadata_dict)

    logger.info('Validating metadata JSON with JSON schema')
    file_utils.validate_json_with_schema(inlined_metadata_file_path)

    sqlite_file_path = working_directory.joinpath(f'{dataset_name}.db')
    __insert_data_csv_into_sqlite(sqlite_file_path, enriched_data_file_path)

    logger.info(f'OK - reading dataset "{dataset_name}"')


class InvalidDataException(Exception):
    def __init__(self, message: str, data_errors: list):
        self.data_errors = data_errors
        Exception.__init__(self, message)
