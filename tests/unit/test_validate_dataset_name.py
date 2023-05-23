import pytest

from microdata_validator import validate_dataset_name
from microdata_validator.exceptions import InvalidDatasetName


def test_validate_dataset_name():
    validate_dataset_name("MITT_DATASET")
    validate_dataset_name("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    validate_dataset_name("A123456789")
    validate_dataset_name("B1A_2Z3_334_567_GHJ")

    with pytest.raises(InvalidDatasetName):
        validate_dataset_name("_LEADING_UNDERSCORE")
    with pytest.raises(InvalidDatasetName):
        validate_dataset_name("1LEADING_NUMBER")
    with pytest.raises(InvalidDatasetName):
        validate_dataset_name("ÆØÅ")
    with pytest.raises(InvalidDatasetName):
        validate_dataset_name("MY-!DÅTÆSØT-!?")
    with pytest.raises(InvalidDatasetName):
        validate_dataset_name("MY.DATASET-!?")
