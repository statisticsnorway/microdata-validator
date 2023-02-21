import logging
from pathlib import Path

from microdata_validator.adapter import local_storage
from microdata_validator.components import (
    temporal_attributes, unit_type_variables
)
from microdata_validator.model import validate_metadata_model


logger = logging.getLogger()


def _insert_centralized_variable_definitions(metadata: dict):
    metadata['identifierVariables'] = [unit_type_variables.get(
        metadata['identifierVariables'][0]['unitType']
    )]
    measure_variable = metadata['measureVariables'][0]
    if 'unitType' in measure_variable:
        insert_measure = unit_type_variables.get(measure_variable['unitType'])
        insert_measure['name'] = measure_variable['name']
        insert_measure['description'] = measure_variable['description']
        metadata['measureVariables'] = [insert_measure]
    temporality_type = metadata['temporalityType']
    metadata['attributeVariables'] = [
        temporal_attributes.generate_start_time_attribute(temporality_type),
        temporal_attributes.generate_stop_time_attribute(temporality_type)
    ] + metadata.get('attributeVariables', [])


def run_reader(
    dataset_name: str,
    working_directory: Path,
    metadata_dict: dict
) -> None:
    logger.debug('Validating metadata JSON with JSON schema')
    validate_metadata_model(metadata_dict)
    _insert_centralized_variable_definitions(metadata_dict)
    metadata_dict['shortName'] = dataset_name
    metadata_dict['measureVariables'][0]['shortName'] = dataset_name

    logger.debug('Writing inlined metadata JSON file to working directory')
    local_storage.write_json(
        working_directory / f'{dataset_name}.json', metadata_dict
    )
