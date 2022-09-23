from typing import Union

from microdata_validator.exceptions import UnregisteredUnitTypeError

# When updating this dictionary remember to also
# update the DatasetMetadataSchema with the
# same key value in the enum for unitTypeType
UNIT_ID_TYPE_FOR_UNIT_TYPE = {
    "JOBB": "JOBBID_1",
    "KJORETOY": "KJORETOY_ID",
    "FAMILIE": "FNR",
    "FORETAK": "ORGNR",
    "HUSHOLDNING": "FNR",
    "KOMMUNE": None,
    "KURS": "KURSID",
    "PERSON": "FNR",
    "VIRKSOMHET": "ORGNR"
}


def get_unit_id_type_for_unit_type(unit_type: str) -> Union[str, None]:
    try:
        return UNIT_ID_TYPE_FOR_UNIT_TYPE[unit_type]
    except KeyError as e:
        raise UnregisteredUnitTypeError(f'No such unit type: {str(e)}') from e
