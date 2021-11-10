import dataset_reader
import dataset_validator
import logging

logger = logging.getLogger()


def validate(dataset_name: str,
             working_directory: str = '/',
             print_errors_to_file: bool = False) -> bool:
    try:
        dataset_reader.run_reader(working_directory, dataset_name)
        data_errors = dataset_validator.run_validator()
        if data_errors:
            print("There were data errors")
            if print_errors_to_file:
                print("Printing errors to file")
            return False
        else:
            print("Dataset files are valid")
            return True
    except Exception as e:
        print(str(e))



__all__ = ['validate']