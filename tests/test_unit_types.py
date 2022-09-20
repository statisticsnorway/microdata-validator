import pytest
from microdata_validator import unit_types


def test_get_unit_id_type_for_unit_type():
    assert unit_types.get_unit_id_type_for_unit_type("PERSON") == "FNR"


def test_none_for_unit_type():
    assert unit_types.get_unit_id_type_for_unit_type("KOMMUNE") is None


def test_get_unit_id_type_for_unknown_unit_type():
    with pytest.raises(unit_types.UnregisteredUnitTypeError) as e:
        unit_types.get_unit_id_type_for_unit_type("SOMETHING")
    assert "No such unit type" in str(e)
