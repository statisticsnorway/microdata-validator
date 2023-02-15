import os
import json
import string
import logging
from pathlib import Path

from jsonschema import validate
from microdata_validator.schema.metadata import Metadata
from microdata_validator.adapter import local_storage
from microdata_validator.exceptions import (
    ParseMetadataError, InvalidDatasetName
)


logger = logging.getLogger()


def validate_with_schema(metadata_json: dict) -> None:
    try:
        Metadata(**metadata_json)
    except Exception as e:
        logger.exception(e)
        raise e


def validate_dataset_name(dataset_name: str) -> None:
    valid_characters = (
        string.ascii_uppercase + string.digits + '_'
    )
    if not all([character in valid_characters for character in dataset_name]):
        raise InvalidDatasetName(
            f'"{dataset_name}" contains invalid characters. '
            'Please use only uppercase A-Z, numbers 0-9 or "_"'
        )


def inline_metadata_references(metadata_file_path: Path,
                               metadata_ref_directory: Path) -> dict:
    def recursive_ref_insert(metadata_object: dict):
        for key, value in metadata_object.items():
            if isinstance(value, dict):
                if "$ref" in value:
                    metadata_object[key] = local_storage.load_json(
                        metadata_ref_directory / Path(value["$ref"])
                    )
                else:
                    recursive_ref_insert(value)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        if "$ref" in item:
                            value[index] = local_storage.load_json(
                                metadata_ref_directory / Path(item["$ref"])
                            )
                        else:
                            recursive_ref_insert(item)

    if metadata_ref_directory is None:
        raise ParseMetadataError("No supplied reference directory")
    if not os.path.isdir(metadata_ref_directory):
        raise ParseMetadataError(
            "Supplied reference directory is invalid"
            f" '{metadata_ref_directory}'"
        )
    logger.debug(f'Reading metadata from file "{metadata_file_path}"')
    metadata: dict = local_storage.load_json(metadata_file_path)
    recursive_ref_insert(metadata)
    return metadata
