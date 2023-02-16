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
