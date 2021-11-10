import csv
import datetime
import os
from shutil import copyfile
import logging

from datastore_builder.common import dataset_utils


logger = logging.getLogger()


#####################
### Usage example ###
#####################
# from common.config_provider import ConfigProvider
# conf = ConfigProvider.get_config()
# dsr = DatasetReader(conf, "KREFTREG_DS")
# dsr.run_reader()

"""Expected catalog structure for input data and metadata:
    <data_input_root catalog>
        /DataSet
            /DATASET_A
                DATASET_A.json
                DATASET_A.csv
            /DATASET_B
                DATASET_B.json
                DATASET_B.csv
            /DATASET_<XX>
        /Attribute
        /Identifier
        /SubjectField
        /UnitType
        /ValueDomain
"""

# TODO: Støtte for "dry-runs" (validere datafil og metadata-fil,
#       men uten at det lastes inn i datastore)
# TODO: Legges inn i kall til denne modulen fra "reader_wrapper.py"
# TODO: Støtte for attributes???
# TODO: Skrive .MD-dokumentasjon for denne modulen.
# TODO: Støtte for pseudonymisering???


def __inline_metadata_references(dataset_metadata_file: dict,
                                 data_input_root_path: str) -> dict:
    """
    Read the dataset JSON metadata file and include metadata-elements
    from external JSON-documents if "$ref" elements exists,
    eg. "$ref" to JSON metadata for ValueDomain, Identifier, SubjectFields, ...
    """
    logger.info(
        f'Reading metadata from file "{dataset_metadata_file}"'
    )
    metadata = dataset_utils.read_json_file(dataset_metadata_file)

    if "$ref" in metadata["unitType"]:
        ref_to_unit_type = str(metadata["unitType"]["$ref"])
        metadata["unitType"] = dataset_utils.read_json_file(
            f"{data_input_root_path}/{ref_to_unit_type}"
        )

    identifier_variable = [
        variable for variable in metadata["variables"]
        if variable.get("variableRole") == "IDENTIFIER"
    ]
    if len(identifier_variable) > 0 and "$ref" in identifier_variable[0]:
        ref_to_identifier = identifier_variable[0]["$ref"]
        identifier_variable[0].update(
            dataset_utils.read_json_file(
                f"{data_input_root_path}/{ref_to_identifier}"
            )
        )
        identifier_variable[0].pop("$ref")  # remove old "$ref"

    measure_variable = [
        variable for variable in metadata["variables"]
        if variable.get("variableRole") == "MEASURE"
    ]
    if len(measure_variable) > 0:
        for subject_field in measure_variable[0].get("subjectFields"):
            if "$ref" in subject_field:
                ref_to_subject_field = subject_field["$ref"]
                subject_field.update(
                    dataset_utils.read_json_file(
                        f"{data_input_root_path}/{ref_to_subject_field}"
                    )
                )
                subject_field.pop("$ref")  # remove old "$ref"

        value_domain = measure_variable[0].get("valueDomain")
        if "$ref" in value_domain:
            ref_to_value_domain = value_domain["$ref"]
            value_domain.update(
                dataset_utils.read_json_file(
                    f"{data_input_root_path}/{ref_to_value_domain}"
                )
            )
            value_domain.pop("$ref")  # remove old "$ref"
            if "sentinelAndMissingValues" in value_domain:
                # If "sentinelAndMissingValues" exists in JSON then move it to the end of valueDomain for better human readability
                sentinel_and_missing_values = value_domain.pop(
                    "sentinelAndMissingValues"
                )
                value_domain.update({
                    "sentinelAndMissingValues": sentinel_and_missing_values
                })

    start_time_variable = [
        variable for variable in metadata["variables"]
        if variable.get("variableRole") == "START_TIME"
    ]
    if len(start_time_variable) > 0 and "$ref" in start_time_variable[0]:
        ref_to_start_time = start_time_variable[0]["$ref"]
        start_time_variable[0].update(
            dataset_utils.read_json_file(
                f"{data_input_root_path}/{ref_to_start_time}"
            )
        )
        start_time_variable[0].pop("$ref")  # remove old "$ref"

    stop_time_variable = [
        variable for variable in metadata["variables"]
        if variable.get("variableRole") == "STOP_TIME"
    ]
    if len(stop_time_variable) > 0 and "$ref" in stop_time_variable[0]:
        ref_to_stop_time = stop_time_variable[0]["$ref"]
        stop_time_variable[0].update(
            dataset_utils.read_json_file(
                f"{data_input_root_path}/{ref_to_stop_time}"
            )
        )
        stop_time_variable[0].pop("$ref")  # remove old "$ref"

    return metadata


def __insert_data_csv_into_sqlite(sqlite_file_path, dataset_data_file,
                                  field_separator=";") -> None:
    db_conn, cursor = dataset_utils.create_temp_sqlite_db_file(
        sqlite_file_path
    )
    with open(file=dataset_data_file, newline='', encoding='utf-8') as f:
        #csv.register_dialect('my_dialect', delimiter=';', quoting=csv.QUOTE_NONE)
        reader = csv.reader(f, delimiter=field_separator)
        cursor.executemany(
            "INSERT INTO temp_dataset "
            "(unit_id, value, start, stop, attributes) "
            "VALUES (?, ?, ?, ?, ?)",
            reader
        )
    db_conn.commit()
    db_conn.close()
    logger.info(
        f'Done reading datafile "{dataset_data_file}" '
        'into temp Sqlite database table.'
    )


def __validate_and_parse_for_temporal_data(data_file_path, field_separator=";",
                                           data_error_limit: int = 100) -> dict:
    data_errors = []  # used for error-reporting
    start_dates = []
    stop_dates = []
    rows_validated = 0

    logger.info(
        f'Validate datafile "{data_file_path}"'
    )
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
                    for data_error in data_errors:
                        logger.error(f"{data_error}")
                    raise InvalidDataException(f"{data_error}")

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
                    #TODO: validate "attributes"?

                    # find temporalCoverage from datafile
                    start_dates.append(str(start).strip('"'))
                    stop_dates.append(str(stop).strip('"'))
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
        for data_error in data_errors:
            logger.error(f"{data_error}")
        raise InvalidDataException(
            f'{data_error}'
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
        f'Append temporal coverage (start, stop, status dates) to metadata'
    )
    if metadata["temporalityType"] in ("FIXED", "EVENT", "ACCUMULATED"):
        metadata["dataRevision"]["temporalCoverageStart"] = (
            temporal_data["start"]
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


def run_reader(config: dict, dataset_name: str) -> None:
    data_input_root_dir = config['DATA_INPUT_ROOT_DIR']
    working_dir = config['WORKING_DIR']

    dataset_metadata_file = (
        f"{data_input_root_dir}/DataSet/{dataset_name}/{dataset_name}.json"
    )
    dataset_data_file = (
        f"{data_input_root_dir}/DataSet/{dataset_name}/{dataset_name}.csv"
    )
    logger.info(f'Start reading dataset "{dataset_name}"')

    metadata_dict = __inline_metadata_references(
        dataset_metadata_file, data_input_root_dir
    )

    temporal_data = __validate_and_parse_for_temporal_data(dataset_data_file)
    __metadata_update_temporal_coverage(metadata_dict, temporal_data)
    logger.info(f'Writing metadata JSON file to working directory')
    temp_metadata_json_file = f"{working_dir}/{dataset_name}.json"
    dataset_utils.write_json_file(metadata_dict, temp_metadata_json_file)

    sqlite_file_path = f"{working_dir}/{dataset_name}.db"
    __insert_data_csv_into_sqlite(sqlite_file_path, dataset_data_file)

    logger.info(
        f'Validating metadata JSON file in working directory with JSON Schema'
    )
    dataset_utils.is_json_file_valid(
        temp_metadata_json_file,
        f"datastore_builder/common/DataSetMetadataSchema.json"
    )
    target_file = f"{working_dir}/{dataset_name}.csv"
    if os.path.exists(target_file):
        os.remove(target_file)
    copyfile(dataset_data_file, target_file)
    logger.info(f'Copied data file to working directory')
    logger.info(f'OK - reading dataset "{dataset_name}"')


class InvalidDataException(Exception):
    pass