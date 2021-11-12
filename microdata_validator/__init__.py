from microdata_validator import dataset_reader
from microdata_validator import dataset_validator
import logging
from pathlib import Path
import uuid
import os


logger = logging.getLogger()


def validate(dataset_name: str,
             working_directory: str = '',
             input_directory: str = '',
             keep_generated_files: bool = False,
             print_errors_to_file: bool = False) -> bool:
    if working_directory:
        working_directory_path = Path(working_directory)
    else:
        working_directory_path = Path(str(uuid.uuid4()))
        os.mkdir(working_directory_path)
    input_directory_path = Path(input_directory)

    try:
        dataset_reader.run_reader(
            working_directory_path, input_directory_path, dataset_name
        )
        data_errors = dataset_validator.run_validator(
            working_directory_path, dataset_name
        )
        if print_errors_to_file:
            print("errors to file")
        return data_errors
    except Exception as e:
        print(str(e))


__all__ = ['validate']
