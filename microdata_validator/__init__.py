import os
import logging
import string
from typing import List, Union
from pathlib import Path

from microdata_validator.model import validate_metadata_model
from microdata_validator.adapter import local_storage
from microdata_validator.components import unit_id_types
from microdata_validator.steps import (
    dataset_reader, dataset_validator, metadata_reader, metadata_inliner
)
from microdata_validator.exceptions import (
    InvalidDatasetException,
    InvalidDatasetName
)

logger = logging.getLogger()


def validate(
    dataset_name: str,
    working_directory: str = '',
    input_directory: str = '',
    keep_temporary_files: bool = False,
    metadata_ref_directory: str = None
) -> List[str]:
    """
    Validate a dataset and return a list of errors.
    If the dataset is valid, the list will be empty.
    """
    # validate dataset name
    try:
        validate_dataset_name(dataset_name)
    except InvalidDatasetName as e:
        return [str(e)]

    # Generate working directory if not supplied
    working_directory_path, working_directory_was_generated = (
         local_storage.resolve_working_directory(working_directory)
    )
    # Make paths for input and ref directory
    input_directory_path = Path(input_directory)
    if metadata_ref_directory is not None:
        metadata_ref_directory = Path(metadata_ref_directory)

    # Run readers and validator
    data_errors = []
    unexpected_exception_occured = False
    try:
        metadata_file_path = (
            input_directory_path / dataset_name / f'{dataset_name}.json'
        )
        metadata_dict = metadata_inliner.run_inliner(
            metadata_file_path,
            metadata_ref_directory
        )
        metadata_reader.run_reader(
            dataset_name,
            working_directory_path,
            metadata_dict
        )
        dataset_reader.run_reader(
            dataset_name,
            working_directory_path,
            input_directory_path
        )
        data_errors = dataset_validator.run_validator(
            working_directory_path, dataset_name
        )
    except InvalidDatasetException as e:
        data_errors = e.errors
    except Exception as e:
        # Raise unexpected exceptions to user
        unexpected_exception_occured = True
        raise e
    finally:
        # Delete temporary files
        if not keep_temporary_files or unexpected_exception_occured:
            local_storage.clean_up_temporary_files(
                dataset_name,
                working_directory_path,
                delete_working_directory=working_directory_was_generated
            )
    return data_errors


def validate_metadata(
    dataset_name: str,
    input_directory: str = '',
    metadata_ref_directory: str = None,
    working_directory: str = '',
    keep_temporary_files: bool = False
) -> List[dict]:
    """
    Validate metadata and return a list of errors.
    If the metadata is valid, the list will be empty.
    """
    data_errors = []

    # validate dataset name
    try:
        validate_dataset_name(dataset_name)
    except InvalidDatasetName as e:
        return [str(e)]

    # Generate working directory if not supplied
    working_directory_path, working_directory_was_generated = (
         local_storage.resolve_working_directory(working_directory)
    )

    # Make paths for input and ref directory
    input_directory_path = Path(input_directory)
    if metadata_ref_directory is not None:
        metadata_ref_directory = Path(metadata_ref_directory)

    try:
        metadata_file_path = (
            input_directory_path / dataset_name / f'{dataset_name}.json'
        )
        metadata_dict = metadata_inliner.run_inliner(
            metadata_file_path,
            metadata_ref_directory
        )
        metadata_reader.run_reader(
            dataset_name,
            working_directory_path,
            metadata_dict
        )
    except InvalidDatasetException as e:
        data_errors = e.errors
    except InvalidDatasetName as e:
        data_errors = [str(e)]
    except Exception as e:
        # Raise unexpected exceptions to user
        raise e
    finally:
        # Delete temporary files
        if not keep_temporary_files:
            local_storage.clean_up_temporary_files(
                dataset_name,
                working_directory_path,
                delete_working_directory=working_directory_was_generated
            )
    return data_errors


def inline_metadata(
    metadata_file_path: str,
    metadata_ref_directory: str,
    output_file_path: str = None
) -> Path:
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
            f"{metadata_file_path.strip('.json')}_INLINED.json"
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
    metadata_dict = metadata_inliner.run_inliner(
        metadata_file_path, metadata_ref_directory
    )
    validate_metadata_model(metadata_dict)

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
    valid_characters = (
        string.ascii_uppercase + string.digits + '_'
    )
    if not all([character in valid_characters for character in dataset_name]):
        raise InvalidDatasetName(
            f'"{dataset_name}" contains invalid characters. '
            'Please use only uppercase A-Z, numbers 0-9 or "_"'
        )
    if dataset_name[0] in string.digits + '_':
        raise InvalidDatasetName(
            f'"{dataset_name}" has a leading number or _.'
            'Please start dataset names with an upper case character A-Z'
        )


__all__ = [
    "validate",
    "validate_metadata",
    "validate_dataset_name",
    "inline_metadata",
    "get_unit_id_type_for_unit_type"
]
