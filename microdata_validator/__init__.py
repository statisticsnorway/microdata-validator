import uuid
import os
import shutil
import logging
from typing import List, Union
from pathlib import Path
from jsonschema import ValidationError

from microdata_validator import schema
from microdata_validator.repository import local_storage
from microdata_validator.components import unit_id_types
from microdata_validator.steps import (
    dataset_reader, dataset_validator
)
from microdata_validator.exceptions import (
    InvalidDataException,
    InvalidDatasetName
)

logger = logging.getLogger()


def validate(
    dataset_name: str,
    working_directory: str = "",
    input_directory: str = "",
    keep_temporary_files: bool = False,
    metadata_ref_directory: str = None
) -> List[str]:
    """
    Validate a dataset and return a list of errors.
    If the dataset is valid, the list will be empty.
    """
    try:
        validate_dataset_name(dataset_name)
    except InvalidDatasetName as e:
        return [str(e)]

    # Generate working directory if not supplied
    if working_directory:
        generated_working_directory = False
        working_directory_path = Path(working_directory)
    else:
        generated_working_directory = True
        working_directory_path = Path(str(uuid.uuid4()))
        os.mkdir(working_directory_path)

    # Make paths for input and ref directory
    input_directory_path = Path(input_directory)
    if metadata_ref_directory is not None:
        metadata_ref_directory = Path(metadata_ref_directory)

    # Run reader and validator
    data_errors = []
    try:
        dataset_reader.run_reader(
            working_directory_path,
            input_directory_path,
            metadata_ref_directory,
            dataset_name,
        )
        data_errors = dataset_validator.run_validator(
            working_directory_path, dataset_name
        )
    except InvalidDataException as e:
        data_errors = e.data_errors
    except ValidationError as e:
        schema_path = ".".join([str(path) for path in e.relative_schema_path])
        data_errors = [f"{schema_path}: {e.message}"]
    except Exception as e:
        # Raise unexpected exceptions to user
        raise e

    # Delete temporary files
    if not keep_temporary_files:
        generated_files = [
            f"{dataset_name}.csv",
            f"{dataset_name}.json",
            f"{dataset_name}.db",
        ]
        if generated_working_directory:
            temporary_files = os.listdir(working_directory_path)
            unknown_files = [
                file for file in temporary_files if file not in generated_files
            ]
            if not unknown_files:
                try:
                    shutil.rmtree(working_directory_path)
                except Exception as e:
                    logger.error(
                        "An exception occured while attempting to delete"
                        f"temporary files: {e}"
                    )
            else:
                for file in generated_files:
                    try:
                        os.remove(working_directory_path / file)
                    except FileNotFoundError:
                        logger.error(
                            f"Could not find file {file} in working directory "
                            "when attempting to delete temporary files."
                        )
        else:
            for file in generated_files:
                try:
                    os.remove(working_directory_path / file)
                except FileNotFoundError:
                    logger.error(
                        f"Could not find file {file} in working directory "
                        "when attempting to delete temporary files."
                    )
    return data_errors


def validate_metadata(metadata_file_path: str,
                      metadata_ref_directory: str = None) -> list:
    """
    Validate a metadata file and return a list of errors.
    If the metadata is valid, the list will be empty.
    """
    try:
        dataset_name = metadata_file_path.split('/')[-1][:-5]
        validate_dataset_name(dataset_name)
        metadata_file_path = Path(metadata_file_path)
        if metadata_ref_directory is None:
            metadata_dict = local_storage.load_json(Path(metadata_file_path))
        else:
            metadata_ref_directory = Path(metadata_ref_directory)
            metadata_dict = schema.inline_metadata_references(
                metadata_file_path, metadata_ref_directory
            )
        schema.validate_with_schema(metadata_dict)
        return []
    except ValidationError as e:
        schema_path = ".".join([str(path) for path in e.relative_schema_path])
        return [f"{schema_path}: {e.message}"]
    except InvalidDatasetName as e:
        return [str(e)]


def inline_metadata(metadata_file_path: str, metadata_ref_directory: str,
                    output_file_path: str = None) -> Path:
    """
    Generate a metadata file with inlined references from a supplied
    metadata file and a reference directory.
    Returns the path to the generated file.
    Throws an error if the metadata is invalid.
    """
    dataset_name = metadata_file_path.split('/')[-1][:-5]
    validate_dataset_name(dataset_name)
    if output_file_path is None:
        output_file_path = Path(
            f"{metadata_file_path.strip('.json')}_inlined.json"
        )
    else:
        output_file_path = Path(output_file_path)
    if os.path.exists(output_file_path):
        raise FileExistsError(
            f"File already exists at '{output_file_path}'. "
            f"Can not overwrite existing file."
        )

    metadata_file_path = Path(metadata_file_path)
    metadata_ref_directory = Path(metadata_ref_directory)
    metadata_dict = schema.inline_metadata_references(
        metadata_file_path, metadata_ref_directory
    )
    schema.validate_with_schema(metadata_dict)

    local_storage.write_json(output_file_path, metadata_dict)
    return output_file_path


def get_unit_id_type_for_unit_type(unit_id: str) -> Union[str, None]:
    """
    Returns the unitIdType for the supplied unitType. Returns None
    if supplied unitType has no attached unitIdType.
    Raises a UnregisteredUnitTypeError on unregistered unitType.
    """
    return unit_id_types.get_unit_id_type_for_unit_type(unit_id)


def validate_dataset_name(dataset_name: str) -> None:
    """
    Validates that the name of the dataset only contains valid
    characters (uppercase A-Z, numbers 0-9 and _)
    """
    schema.validate_dataset_name(dataset_name)


__all__ = [
    "validate",
    "validate_metadata",
    "validate_dataset_name",
    "inline_metadata",
    "get_unit_id_type_for_unit_type"
]
