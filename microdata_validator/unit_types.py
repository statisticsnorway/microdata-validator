from typing import Union


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


def is_valid_unit_type(unit_type: str) -> bool:
    return unit_type in UNIT_ID_TYPE_FOR_UNIT_TYPE


def get_unit_id_type_for_unit_type(unit_type: str) -> Union[str, None]:
    return UNIT_ID_TYPE_FOR_UNIT_TYPE[unit_type]
