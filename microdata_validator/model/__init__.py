# pylint: disable=raise-missing-from
import logging

from pydantic import ValidationError

from microdata_validator.exceptions import InvalidDatasetException
from microdata_validator.model.metadata import Metadata


logger = logging.getLogger()


def validate_metadata_model(metadata_json: dict) -> None:
    try:
        Metadata(**metadata_json)
    except ValidationError as e:
        logger.exception(e)
        error_messages = []
        for error in e.errors():
            location = '->'.join(
                loc for loc in error['loc']
                if loc != '__root__' and not isinstance(loc, int)
            )
            error_messages.append(f'{location}: {error["msg"]}')
        raise InvalidDatasetException(
            'Invalid metadata file', errors=error_messages
        )
    except Exception as e:
        logger.exception(e)
        raise e
