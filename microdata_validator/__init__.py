from microdata_validator import dataset_reader
from microdata_validator import dataset_validator
from microdata_validator.dataset_reader import InvalidDataException
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
    except InvalidDataException as e:
        data_errors = e.data_errors
    except ValidationError as e:
        schema_path = '.'.join(e.relative_schema_path)
        data_errors = [f"{schema_path}: {e.message}"]
    except Exception as e:
        # Raise unexpected exceptions to user
        raise e

    if delete_working_directory:
        generated_files = [
            working_directory_path / f"{dataset_name}.csv",
            working_directory_path / f"{dataset_name}.json",
            working_directory_path / f"{dataset_name}.db"
        ]

        for file in generated_files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
    return data_errors


__all__ = ['validate']
