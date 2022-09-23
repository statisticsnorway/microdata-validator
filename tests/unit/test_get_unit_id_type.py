import pytest
from microdata_validator import get_unit_id_type_for_unit_type
from microdata_validator.exceptions import UnregisteredUnitTypeError


def test_get_unit_id_type_for_unit_type():
    assert get_unit_id_type_for_unit_type("PERSON") == "FNR"


def test_none_for_unit_type():
    assert get_unit_id_type_for_unit_type("KOMMUNE") is None


def test_get_unit_id_type_for_unknown_unit_type():
    with pytest.raises(UnregisteredUnitTypeError) as e:
        get_unit_id_type_for_unit_type("SOMETHING")
    assert "No such unit type" in str(e)
