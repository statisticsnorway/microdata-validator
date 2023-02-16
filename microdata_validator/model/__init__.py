import logging

from pydantic import ValidationError

from microdata_validator.model.metadata import Metadata


logger = logging.getLogger()


def validate_metadata_model(metadata_json: dict) -> None:
    try:
        Metadata(**metadata_json)
    except ValidationError as e:
        logger.exception(e)
        raise e
    except Exception as e:
        logger.exception(e)
        raise e
