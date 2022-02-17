from microdata_validator import dataset_reader
from microdata_validator import dataset_validator
import logging
from jsonschema import ValidationError
from pathlib import Path
import uuid
import os


logger = logging.getLogger()


def validate(dataset_name: str,
             working_directory: str = '',
             input_directory: str = '',
             delete_working_directory: bool = False,
             print_errors_to_file: bool = False) -> bool:

    if working_directory:
        working_directory_path = Path(working_directory)
    else:
        working_directory_path = Path(str(uuid.uuid4()))
        os.mkdir(working_directory_path)
    input_directory_path = Path(input_directory)

    data_errors = []
    try:
        dataset_reader.run_reader(
            working_directory_path, input_directory_path, dataset_name
        )
        data_errors = dataset_validator.run_validator(
            working_directory_path, dataset_name
        )
        if print_errors_to_file:
            print("errors to file")
    except ValidationError as e:
        schema_path = '.'.join(e.relative_schema_path)
        data_errors = [f"{schema_path}: {e.message}"]
    except Exception as e:
        # Raise unexpected exceptions to user
        raise e
    
    if delete_working_directory:
        for file in os.listdir(working_directory_path):
            os.remove(working_directory_path / file)
    
    return data_errors

__all__ = ['validate']
