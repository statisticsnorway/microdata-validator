import os
import logging
from pathlib import Path
from microdata_validator.repository import local_storage

logger = logging.getLogger()


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
            elif isinstance(value, str) and key == "$ref":
                print(f"FOUND VALUE: {value}")

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


class ParseMetadataError(Exception):
    pass
