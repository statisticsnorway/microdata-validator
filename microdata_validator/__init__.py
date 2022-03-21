from microdata_validator import dataset_reader
from microdata_validator import dataset_validator
from microdata_validator import utils
from microdata_validator.dataset_reader import InvalidDataException
import logging
from jsonschema import ValidationError
from pathlib import Path
import uuid
import os
import shutil

logger = logging.getLogger()


def validate(dataset_name: str,
             working_directory: str = '',
             input_directory: str = '',
             keep_temporary_files: bool = False,
             metadata_ref_directory: str = None,
             print_errors_to_file: bool = False) -> bool:

    if working_directory:
        generated_working_directory = False
        working_directory_path = Path(working_directory)
    else:
        generated_working_directory = True
        working_directory_path = Path(str(uuid.uuid4()))
        os.mkdir(working_directory_path)

    input_directory_path = Path(input_directory)
    if metadata_ref_directory is not None:
        metadata_ref_directory = Path(metadata_ref_directory)

    data_errors = []
    try:
        dataset_reader.run_reader(
            working_directory_path,
            input_directory_path,
            metadata_ref_directory,
            dataset_name
        )
        data_errors = dataset_validator.run_validator(
            working_directory_path, dataset_name
        )
        if print_errors_to_file:
            print("errors to file")
    except InvalidDataException as e:
        data_errors = e.data_errors
    except ValidationError as e:
        schema_path = '.'.join([str(path) for path in e.relative_schema_path])
        data_errors = [f"{schema_path}: {e.message}"]
    except Exception as e:
        # Raise unexpected exceptions to user
        raise e

    if not keep_temporary_files:
        generated_files = [
            f"{dataset_name}.csv",
            f"{dataset_name}.json",
            f"{dataset_name}.db"
        ]
        if generated_working_directory:
            temporary_files = os.listdir(working_directory_path)
            unknown_files = [
                file for file in temporary_files
                if file not in generated_files
            ]
            if not unknown_files:
                shutil.rmtree(working_directory_path)
        else:
            for file in generated_files:
                try:
                    os.remove(working_directory_path / file)
                except FileNotFoundError:
                    pass
    return data_errors


def validate_metadata(metadata_file_path: str,
                      metadata_ref_directory: str = None) -> list:
    try:
        metadata_file_path = Path(metadata_file_path)
        if metadata_ref_directory is None:
            metadata_dict = utils.load_json(Path(metadata_file_path))
        else:
            metadata_ref_directory = Path(metadata_ref_directory)
            metadata_dict = utils.inline_metadata_references(
                metadata_file_path, metadata_ref_directory
            )
        utils.validate_json_with_schema(metadata_dict)
        return []
    except ValidationError as e:
        schema_path = '.'.join([str(path) for path in e.relative_schema_path])
        return [f"{schema_path}: {e.message}"]


def inline_metadata(metadata_file_path: str, metadata_ref_directory: str,
                    output_file_path: str = None) -> Path:
    if output_file_path is None:
        output_file_path = Path(
            f"{metadata_file_path.strip('.json')}_inlined.json"
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
    metadata_dict = utils.inline_metadata_references(
        metadata_file_path, metadata_ref_directory
    )
    utils.validate_json_with_schema(metadata_dict)

    utils.write_json(output_file_path, metadata_dict)
    return output_file_path


__all__ = ['validate', 'validate_metadata', 'inline_metadata']
