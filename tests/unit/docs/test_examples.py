from microdata_validator import validate


INPUT_DIRECTORY = "docs/examples"
EXAMPLE_DATASETS = [
    "SYNT_BEFOLKNING_KJOENN",
    "SYNT_BEFOLKNING_SIVSTAND",
    "SYNT_PERSON_INNTEKT",
]


def test_validate_valid_dataset():
    for dataset_name in EXAMPLE_DATASETS:
        data_errors = validate(dataset_name, input_directory=INPUT_DIRECTORY)
        assert not data_errors
