from microdata_validator.exceptions import InvalidIdentifierType


IDENTIFIER_VARIABLES = {
    "PERSON": {
        "shortName": "PERSON",
        "name": [{"languageCode": "no", "value": "Person"}],
        "description": [
            {
                "languageCode": "no",
                "value": "Identifikator for person i Microdata"
            }
        ],
        "dataType": "STRING",
        "unitType": {
            "shortName": "PERSON",
            "name": [{"languageCode": "no", "value": "Person"}],
            "description": [
                {
                    "languageCode": "no",
                    "value": (
                        "Statistisk enhet er person (individ, enkeltmenneske)"
                    )
                }
            ],
        },
        "format": "RandomUInt48",
        "valueDomain": {
            "description": [
                {"languageCode": "no", "value": "Pseudonymisert personnummer"}
            ],
        },
    }
}


def get_from_type(identifier_type: str):
    try:
        return IDENTIFIER_VARIABLES[identifier_type]
    except KeyError as e:
        raise InvalidIdentifierType(identifier_type) from e
